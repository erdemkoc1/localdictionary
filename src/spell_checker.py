import re
import threading
from typing import Optional, List, Tuple
from functools import lru_cache
from src.utils import turkish_lower


_PREFIX_SQL_EN = """
    SELECT DISTINCT en_lower
    FROM bilingual
    WHERE en_lower >= ? AND en_lower < ?
      AND length(en_lower) BETWEEN ? AND ?
    LIMIT 80;
"""

_PREFIX_SQL_TR = """
    SELECT DISTINCT tr_lower
    FROM bilingual
    WHERE tr_lower >= ? AND tr_lower < ?
      AND length(tr_lower) BETWEEN ? AND ?
    LIMIT 80;
"""


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


# Turkish ASCII -> Diacritics mapping pairs for de-asciification
TR_ASCII_VARIANTS = {
    "c": ["c", "ç"],
    "g": ["g", "ğ"],
    "i": ["i", "ı"],
    "o": ["o", "ö"],
    "s": ["s", "ş"],
    "u": ["u", "ü"]
}


def _synchronized(method):
    def wrapped(self, *args, **kwargs):
        with self._db_lock:
            return method(self, *args, **kwargs)
    wrapped.__name__ = method.__name__
    wrapped.__doc__ = method.__doc__
    return wrapped


class SpellChecker:
    """
    Fast, offline spelling and typo correction engine for Dictionary and Sentence translation.
    Features:
    1. Turkish de-asciification (e.g. 'karim' -> 'karım', 'aldatti' -> 'aldattı', 'ogretmen' -> 'öğretmen')
    2. Typo correction via indexed B-tree prefix range and Levenshtein edit distance
    3. Sentence-level typo detection and suggestion
    """
    def __init__(self, db_conn=None, db_lock=None):
        self.conn = db_conn
        self._db_lock = db_lock or threading.RLock()

    @_synchronized
    def _word_exists(self, word: str) -> bool:
        if not self.conn:
            return False
        w_low = turkish_lower(word)
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM bilingual WHERE tr_lower = ? OR en_lower = ? LIMIT 1;",
            (w_low, w_low)
        )
        return bool(cur.fetchone())

    @_synchronized
    def _get_deasciified_candidate(self, word: str) -> Optional[str]:
        """
        Attempts to reconstruct Turkish characters for ASCII-typed words.
        e.g., 'aldatti' -> 'aldattı', 'karim' -> 'karım', 'guzel' -> 'güzel', 'ogretmen' -> 'öğretmen'
        """
        w_low = turkish_lower(word)
        if not self.conn:
            return None

        patterns_to_try = []

        # 1. Ending i -> ı (e.g. 'aldatti' -> 'aldattı', 'karim' -> 'karım')
        if w_low.endswith("i"):
            patterns_to_try.append(w_low[:-1] + "ı")
        last_i = w_low.rfind("i")
        if last_i != -1:
            patterns_to_try.append(w_low[:last_i] + "ı" + w_low[last_i+1:])

        # 2. Individual letter substitutions
        subs = [
            ("u", "ü"), ("o", "ö"), ("c", "ç"), ("s", "ş"), ("g", "ğ"), ("i", "ı")
        ]
        for src_c, dst_c in subs:
            if src_c in w_low:
                patterns_to_try.append(w_low.replace(src_c, dst_c))

        # 3. Two-letter combinations (e.g. 'ogretmen' -> o->ö and g->ğ)
        for i, (s1, d1) in enumerate(subs):
            for s2, d2 in subs[i+1:]:
                if s1 in w_low and s2 in w_low:
                    patterns_to_try.append(w_low.replace(s1, d1).replace(s2, d2))

        # 4. Full substitution
        curr = w_low
        for a, b in subs:
            curr = curr.replace(a, b)
        patterns_to_try.append(curr)

        # Check in database
        cur = self.conn.cursor()
        for cand in patterns_to_try:
            if cand != w_low:
                cur.execute(
                    """
                    SELECT tr_lower FROM bilingual 
                    WHERE tr_lower = ? 
                    ORDER BY CASE WHEN category = 'Common Usage' THEN 0 WHEN category = 'General' THEN 1 ELSE 5 END
                    LIMIT 1;
                    """,
                    (cand,)
                )
                row = cur.fetchone()
                if row:
                    return row[0]

        return None

    @_synchronized
    def get_word_suggestion(self, word: str, is_en: bool = False) -> Optional[str]:
        """
        Returns a spelling suggestion for an isolated word if a typo/misspelling is detected.
        Returns None if word is already valid or no close match found.
        """
        if not word or len(word) < 3 or len(word) > 128 or not self.conn:
            return None

        w_low = turkish_lower(word.strip())

        # If word is already valid in dictionary, no correction needed
        if self._word_exists(w_low):
            return None

        # 1. Try Turkish de-asciification first for non-English queries
        if not is_en:
            deasc = self._get_deasciified_candidate(w_low)
            if deasc:
                return deasc

        # 2. Levenshtein search within adaptive prefix range
        # Try longer prefix first for speed & accuracy, then shorter prefix
        pref_lengths = [max(2, len(w_low) - 2), max(2, len(w_low) - 3)]
        
        cur = self.conn.cursor()
        max_dist = 1 if len(w_low) <= 4 else 2
        min_len = max(1, len(w_low) - max_dist)
        max_len = len(w_low) + max_dist
        query = _PREFIX_SQL_EN if is_en else _PREFIX_SQL_TR

        best_cand = None
        best_dist = 999

        for plen in pref_lengths:
            prefix = w_low[:plen]
            next_prefix = prefix[:-1] + chr(ord(prefix[-1]) + 1)
            cur.execute(query, (prefix, next_prefix, min_len, max_len))
            candidates = [r[0] for r in cur.fetchall()]

            for cand_word in candidates:
                if not cand_word or cand_word == w_low or " " in cand_word:
                    continue
                dist = levenshtein_distance(w_low, cand_word)
                if dist <= max_dist and dist < best_dist:
                    best_dist = dist
                    best_cand = cand_word

            if best_cand:
                break

        return best_cand

    @_synchronized
    def get_sentence_suggestion(self, sentence: str, from_lang: str = "auto") -> Optional[str]:
        """
        Checks words in sentence for typos and missing Turkish diacritics.
        Constructs and returns the corrected sentence if changes were made, otherwise None.
        """
        if not sentence or len(sentence) > 20_000 or "\x00" in sentence or not self.conn:
            return None

        is_en = (from_lang == "en")
        tokens = re.findall(r"\b[\w'-]+\b|[^\w\s]", sentence)
        if not tokens:
            return None

        changed = False
        corrected_tokens = []

        for tok in tokens:
            # Skip punctuation and digits
            if not tok.isalpha():
                corrected_tokens.append(tok)
                continue

            # Check if this token has a correction
            sugg = self.get_word_suggestion(tok, is_en=is_en)
            if sugg and sugg != turkish_lower(tok):
                # Preserve case if original was capitalized
                if tok[0].isupper():
                    sugg = sugg.capitalize()
                corrected_tokens.append(sugg)
                changed = True
            else:
                corrected_tokens.append(tok)

        if not changed:
            return None

        # Reconstruct sentence with proper punctuation spacing
        res = ""
        for i, tok in enumerate(corrected_tokens):
            if i > 0 and tok not in ".,!?;:'\":)":
                prev = corrected_tokens[i-1]
                if prev not in "('\"":
                    res += " "
            res += tok

        return res

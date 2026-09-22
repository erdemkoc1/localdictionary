import re
import sqlite3
from typing import List, Dict, Any, Tuple, Optional
from src.utils import turkish_lower, get_resource_path

# Common English irregular verbs -> (base_lemma, tense)
IRREGULAR_VERBS = {
    "saw": ("see", "past"),
    "seen": ("see", "past_participle"),
    "went": ("go", "past"),
    "gone": ("go", "past_participle"),
    "came": ("come", "past"),
    "took": ("take", "past"),
    "taken": ("take", "past_participle"),
    "gave": ("give", "past"),
    "given": ("give", "past_participle"),
    "found": ("find", "past"),
    "thought": ("think", "past"),
    "told": ("tell", "past"),
    "became": ("become", "past"),
    "left": ("leave", "past"),
    "felt": ("feel", "past"),
    "put": ("put", "past"),
    "brought": ("bring", "past"),
    "began": ("begin", "past"),
    "begun": ("begin", "past_participle"),
    "kept": ("keep", "past"),
    "held": ("hold", "past"),
    "wrote": ("write", "past"),
    "written": ("write", "past_participle"),
    "stood": ("stand", "past"),
    "heard": ("hear", "past"),
    "let": ("let", "past"),
    "meant": ("mean", "past"),
    "set": ("set", "past"),
    "met": ("meet", "past"),
    "paid": ("pay", "past"),
    "sat": ("sit", "past"),
    "spoke": ("speak", "past"),
    "spoken": ("speak", "past_participle"),
    "read": ("read", "past"),
    "grew": ("grow", "past"),
    "lost": ("lose", "past"),
    "fell": ("fall", "past"),
    "fallen": ("fall", "past_participle"),
    "sent": ("send", "past"),
    "built": ("build", "past"),
    "understood": ("understand", "past"),
    "drew": ("draw", "past"),
    "drawn": ("draw", "past_participle"),
    "broke": ("break", "past"),
    "broken": ("break", "past_participle"),
    "spent": ("spend", "past"),
    "cut": ("cut", "past"),
    "rose": ("rise", "past"),
    "risen": ("rise", "past_participle"),
    "drove": ("drive", "past"),
    "driven": ("drive", "past_participle"),
    "bought": ("buy", "past"),
    "wore": ("wear", "past"),
    "worn": ("wear", "past_participle"),
    "chose": ("choose", "past"),
    "chosen": ("choose", "past_participle"),
    "drank": ("drink", "past"),
    "drunk": ("drink", "past_participle"),
    "ate": ("eat", "past"),
    "eaten": ("eat", "past_participle"),
    "ran": ("run", "past"),
    "knew": ("know", "past"),
    "known": ("know", "past_participle")
}

# Pronouns mapping
PRONOUNS_EN_TR = {
    "i": {"tr": "ben", "person": "1s"},
    "you": {"tr": "sen", "person": "2s"},
    "he": {"tr": "o", "person": "3s"},
    "she": {"tr": "o", "person": "3s"},
    "it": {"tr": "o", "person": "3s"},
    "we": {"tr": "biz", "person": "1p"},
    "they": {"tr": "onlar", "person": "3p"},
    "me": {"tr": "beni", "person": "1s"},
    "him": {"tr": "onu", "person": "3s"},
    "her": {"tr": "onu", "person": "3s"},
    "us": {"tr": "bizi", "person": "1p"},
    "them": {"tr": "onları", "person": "3p"},
    "my": {"tr": "benim", "possessive": "1s"},
    "your": {"tr": "senin", "possessive": "2s"},
    "his": {"tr": "onun", "possessive": "3s"},
    "its": {"tr": "onun", "possessive": "3s"},
    "our": {"tr": "bizim", "possessive": "1p"},
    "their": {"tr": "onların", "possessive": "3p"},
    "this": {"tr": "bu", "person": "3s"},
    "that": {"tr": "şu", "person": "3s"},
    "these": {"tr": "bunlar", "person": "3p"},
    "those": {"tr": "şunlar", "person": "3p"}
}

# Prepositions mapping
PREPOSITIONS_EN = {
    "in": {"case": "locative", "suffix": "de", "fallback": "içinde"},
    "at": {"case": "locative", "suffix": "de", "fallback": "yerinde"},
    "on": {"case": "locative", "suffix": "de", "fallback": "üzerinde"},
    "to": {"case": "dative", "suffix": "e", "fallback": "doğru"},
    "from": {"case": "ablative", "suffix": "den", "fallback": "den"},
    "with": {"case": "postposition", "word": "ile"},
    "for": {"case": "postposition", "word": "için"},
    "about": {"case": "postposition", "word": "hakkında"},
    "without": {"case": "postposition", "word": "olmadan"},
    "under": {"case": "postposition", "word": "altında"},
    "before": {"case": "postposition", "word": "önce"},
    "after": {"case": "postposition", "word": "sonra"}
}

TIME_ADVERBS_EN = {
    "today": "bugün",
    "yesterday": "dün",
    "tomorrow": "yarın",
    "now": "şimdi",
    "always": "her zaman",
    "never": "asla",
    "sometimes": "bazen",
    "often": "sık sık",
    "soon": "yakında",
    "later": "sonra",
    "already": "zaten",
    "tonight": "bu gece"
}

CONJUNCTIONS_EN = {
    "and": "ve",
    "or": "veya",
    "but": "ama",
    "because": "çünkü",
    "if": "eğer",
    "so": "bu yüzden",
    "while": "iken"
}

class SyntaxTranslator:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = get_resource_path("data/dictionary.db")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cur = self.conn.cursor()

    def _lookup_word(self, word: str, preferred_pos: Optional[str] = None, is_en: bool = True) -> List[Tuple[str, str, str]]:
        w_lower = turkish_lower(word)
        col = "en_lower" if is_en else "tr_lower"
        tgt_col = "tr" if is_en else "en"

        # If a preferred POS is given (e.g. 'v.' or 'n.' or 'adj.')
        if preferred_pos:
            self.cur.execute(f"""
            SELECT {tgt_col}, type, category 
            FROM bilingual 
            WHERE {col} = ? AND type LIKE ?
            ORDER BY 
                CASE 
                    WHEN category = 'Common Usage' THEN 0 
                    WHEN category = 'General' THEN 1 
                    ELSE 2 
                END 
            LIMIT 5;
            """, (w_lower, f"%{preferred_pos}%"))
            rows = self.cur.fetchall()
            if rows:
                return rows

        self.cur.execute(f"""
        SELECT {tgt_col}, type, category 
        FROM bilingual 
        WHERE {col} = ? 
        ORDER BY 
            CASE 
                WHEN category = 'Common Usage' THEN 0 
                WHEN category = 'General' THEN 1 
                ELSE 2 
            END 
        LIMIT 5;
        """, (w_lower,))
        return self.cur.fetchall()

    def _conjugate_turkish_verb(self, verb_lemma: str, tense: str, person: str = "3s") -> str:
        """Conjugates a Turkish verb lemma with 4-way vowel harmony."""
        if not (verb_lemma.endswith("mek") or verb_lemma.endswith("mak")):
            return verb_lemma

        stem = verb_lemma[:-3] # remove 'mek' or 'mak'
        
        # Determine last vowel in stem for 4-way vowel harmony
        last_vowels = [c for c in stem if c in "aıoueiöü"]
        last_v = last_vowels[-1] if last_vowels else "e"

        # 4-way harmony suffixes:
        # a, ı -> ı
        # e, i -> i
        # o, u -> u
        # ö, ü -> ü
        if last_v in "aı":
            h_vowel = "ı"
        elif last_v in "ei":
            h_vowel = "i"
        elif last_v in "ou":
            h_vowel = "u"
        else: # öü
            h_vowel = "ü"

        # 1. Past Tense (-di/-dı/-du/-dü)
        if tense == "past":
            d_char = "t" if stem[-1] in "fstkçşhp" else "d"
            suffix = f"{d_char}{h_vowel}"
            if person == "1s":
                return f"{stem}{suffix}m"
            elif person == "2s":
                return f"{stem}{suffix}n"
            elif person == "1p":
                return f"{stem}{suffix}k"
            elif person == "3p":
                ler = "ler" if last_v in "eiöü" else "lar"
                return f"{stem}{suffix}{ler}"
            else: # 3s
                return f"{stem}{suffix}"

        # 2. Future Tense (-ecek / -acak)
        elif tense == "future":
            e_char = "e" if last_v in "eiöü" else "a"
            buffer = "y" if stem[-1] in "aıoueiöü" else ""
            if person == "1s":
                end = f"ğeceğim" if e_char == "e" else "ğacağım"
                return f"{stem}{buffer}{end[1:]}"
            elif person == "1p":
                end = f"ğeceğiz" if e_char == "e" else "ğacağız"
                return f"{stem}{buffer}{end[1:]}"
            else:
                return f"{stem}{buffer}{e_char}cek"

        # 3. Present Continuous / General (-iyor / -ıyor / -uyor / -üyor)
        else:
            s = stem
            if s[-1] in "aıoueiöü":
                s = s[:-1]
            suffix = f"{h_vowel}yor"
            if person == "1s":
                return f"{s}{suffix}um"
            elif person == "1p":
                return f"{s}{suffix}uz"
            elif person == "2s":
                return f"{s}{suffix}sun"
            else: # 3s
                return f"{s}{suffix}"

    def translate(self, sentence: str, direction: str = "auto") -> Dict[str, Any]:
        """
        Translates sentence using dictionary lookups, syntax reordering (SVO <-> SOV),
        and contextual grammar rules.
        """
        sentence = sentence.strip()
        if not sentence:
            return {"translated_text": "", "breakdown": []}

        # Auto-detect direction
        tr_chars = set("çğıöşüÇĞİÖŞÜ")
        if direction == "auto":
            direction = "tr_en" if any(c in tr_chars for c in sentence) else "en_tr"

        if direction == "en_tr":
            return self._translate_en_to_tr(sentence)
        else:
            return self._translate_tr_to_en(sentence)

    def _translate_en_to_tr(self, sentence: str) -> Dict[str, Any]:
        raw_tokens = re.findall(r"\b[\w'-]+\b|[.,!?;]", sentence)
        if not raw_tokens:
            return {"translated_text": "", "breakdown": []}

        breakdown = []
        i = 0
        n = len(raw_tokens)
        subject_person = "3s"
        has_future_modal = False

        while i < n:
            token = raw_tokens[i]
            t_lower = token.lower()

            # Punctuation
            if token in ".,!?;":
                breakdown.append({"original": token, "translated": token, "role": "punct", "pos": "punct"})
                i += 1
                continue

            # Conjunctions
            if t_lower in CONJUNCTIONS_EN:
                breakdown.append({"original": token, "translated": CONJUNCTIONS_EN[t_lower], "role": "connector", "pos": "conj"})
                i += 1
                continue

            # Time adverbs
            if t_lower in TIME_ADVERBS_EN:
                breakdown.append({"original": token, "translated": TIME_ADVERBS_EN[t_lower], "role": "time", "pos": "adv"})
                i += 1
                continue

            # Pronouns
            if t_lower in PRONOUNS_EN_TR:
                p_info = PRONOUNS_EN_TR[t_lower]
                if "person" in p_info and t_lower in ["i", "you", "he", "she", "it", "we", "they"]:
                    subject_person = p_info["person"]
                    role = "subject"
                else:
                    role = "object"
                breakdown.append({"original": token, "translated": p_info["tr"], "role": role, "pos": "pronoun"})
                i += 1
                continue

            # Modals (will, can, must)
            if t_lower == "will":
                has_future_modal = True
                i += 1
                continue

            # Preposition phrases (e.g. "in London", "for my brother")
            if t_lower in PREPOSITIONS_EN and i + 1 < n:
                prep = PREPOSITIONS_EN[t_lower]
                
                # Check if next is possessive pronoun (e.g. "for my brother")
                if raw_tokens[i+1].lower() in ["my", "your", "his", "her", "our", "their"] and i + 2 < n:
                    poss = raw_tokens[i+1].lower()
                    noun = raw_tokens[i+2]
                    noun_matches = self._lookup_word(noun, preferred_pos="n.", is_en=True)
                    noun_tr = noun_matches[0][0] if noun_matches else noun
                    
                    # Turkish possessive suffix approximation
                    combined = f"{PRONOUNS_EN_TR[poss]['tr']} {noun_tr} {prep.get('word', 'için')}"
                    breakdown.append({
                        "original": f"{token} {poss} {noun}",
                        "translated": combined,
                        "role": "adverbial",
                        "pos": "prep_phrase"
                    })
                    i += 3
                    continue
                else:
                    noun = raw_tokens[i+1]
                    if noun not in ".,!?;":
                        noun_matches = self._lookup_word(noun, preferred_pos="n.", is_en=True)
                        noun_tr = noun_matches[0][0] if noun_matches else noun
                        if prep.get("case") == "locative":
                            combined = f"{noun_tr}'da" if noun[0].isupper() else f"{noun_tr}da"
                        elif prep.get("case") == "dative":
                            combined = f"{noun_tr}'a" if noun[0].isupper() else f"{noun_tr}a"
                        elif prep.get("case") == "ablative":
                            combined = f"{noun_tr}'dan" if noun[0].isupper() else f"{noun_tr}dan"
                        else:
                            combined = f"{noun_tr} {prep.get('word', '')}"

                        breakdown.append({
                            "original": f"{token} {noun}",
                            "translated": combined,
                            "role": "adverbial",
                            "pos": "prep_phrase"
                        })
                        i += 2
                        continue

            # Articles (a, an, the)
            if t_lower in ["a", "an"]:
                breakdown.append({"original": token, "translated": "bir", "role": "determiner", "pos": "art"})
                i += 1
                continue
            elif t_lower == "the":
                i += 1
                continue

            # Check Irregular Past Verbs
            if t_lower in IRREGULAR_VERBS:
                base_lemma, v_tense = IRREGULAR_VERBS[t_lower]
                matches = self._lookup_word(base_lemma, preferred_pos="v.", is_en=True)
                if matches:
                    tr_lemma = matches[0][0]
                    conjugated = self._conjugate_turkish_verb(tr_lemma, v_tense, subject_person)
                    breakdown.append({
                        "original": token,
                        "translated": conjugated,
                        "role": "verb",
                        "pos": "v.",
                        "alternatives": [m[0] for m in matches[1:3]]
                    })
                    i += 1
                    continue

            # Regular Verbs / Nouns / Adjectives disambiguation based on context
            # If word follows Subject or Modal -> likely VERB
            prev_role = breakdown[-1]["role"] if breakdown else ""
            is_verb_context = (prev_role == "subject" or has_future_modal)
            
            # If preceded by article 'bir' / determiner / adjective -> likely NOUN
            is_noun_context = (prev_role in ["determiner", "adjective"])

            # Check suffix endings for regular verbs (-ed, -s, -ing)
            lemma = token
            tense = "future" if has_future_modal else "present"
            if t_lower.endswith("ed") and len(t_lower) > 4:
                lemma = t_lower[:-2]
                tense = "past"
                is_verb_context = True
            elif t_lower.endswith("s") and len(t_lower) > 3 and is_verb_context:
                lemma = t_lower[:-1]
                tense = "present"
            elif has_future_modal:
                tense = "future"
                is_verb_context = True

            pref_pos = "v." if is_verb_context else ("n." if is_noun_context else None)
            matches = self._lookup_word(lemma, preferred_pos=pref_pos, is_en=True)
            
            if matches:
                top_tr = matches[0][0]
                top_pos = matches[0][1]
                
                # If it's a verb and we need to conjugate it
                if "v." in top_pos or is_verb_context:
                    conjugated = self._conjugate_turkish_verb(top_tr, tense, subject_person)
                    breakdown.append({
                        "original": token,
                        "translated": conjugated,
                        "role": "verb",
                        "pos": "v.",
                        "alternatives": [m[0] for m in matches[1:3]]
                    })
                else:
                    role = "adjective" if "adj." in top_pos else "object"
                    breakdown.append({
                        "original": token,
                        "translated": top_tr,
                        "role": role,
                        "pos": top_pos,
                        "alternatives": [m[0] for m in matches[1:3]]
                    })
            else:
                breakdown.append({"original": token, "translated": token, "role": "object", "pos": "unknown"})

            i += 1

        # Reorder SVO -> SOV (Subject -> Time -> Adverbial -> Object/Adjective -> Verb)
        subjects = [b for b in breakdown if b["role"] == "subject"]
        times = [b for b in breakdown if b["role"] == "time"]
        adverbials = [b for b in breakdown if b["role"] == "adverbial"]
        connectors = [b for b in breakdown if b["role"] == "connector"]
        objects = [b for b in breakdown if b["role"] in ["object", "determiner", "adjective"]]
        verbs = [b for b in breakdown if b["role"] == "verb"]
        puncts = [b for b in breakdown if b["role"] == "punct"]

        reordered = connectors + subjects + times + adverbials + objects + verbs
        words = [b["translated"] for b in reordered if b["translated"]]
        
        sentence_str = " ".join(words)
        if puncts:
            sentence_str += puncts[-1]["original"]

        if sentence_str:
            sentence_str = sentence_str[0].upper() + sentence_str[1:]

        return {
            "translated_text": sentence_str,
            "breakdown": breakdown
        }

    def _translate_tr_to_en(self, sentence: str) -> Dict[str, Any]:
        """Translates Turkish SOV to English SVO sentence."""
        raw_tokens = re.findall(r"\b[\w'-]+\b|[.,!?;]", sentence)
        if not raw_tokens:
            return {"translated_text": "", "breakdown": []}

        breakdown = []
        for token in raw_tokens:
            if token in ".,!?;":
                breakdown.append({"original": token, "translated": token, "role": "punct", "pos": "punct"})
                continue

            matches = self._lookup_word(token, is_en=False)
            if matches:
                top_en = matches[0][0]
                top_pos = matches[0][1]
                role = "verb" if "v." in top_pos else ("subject" if token.lower() in ["ben", "sen", "o", "biz", "onlar"] else "object")
                breakdown.append({
                    "original": token,
                    "translated": top_en,
                    "role": role,
                    "pos": top_pos,
                    "alternatives": [m[0] for m in matches[1:3]]
                })
            else:
                breakdown.append({"original": token, "translated": token, "role": "object", "pos": "unknown"})

        # Turkish SOV -> English SVO reordering (Subject -> Verb -> Object)
        subjects = [b for b in breakdown if b["role"] == "subject"]
        verbs = [b for b in breakdown if b["role"] == "verb"]
        objects = [b for b in breakdown if b["role"] not in ["subject", "verb", "punct"]]
        puncts = [b for b in breakdown if b["role"] == "punct"]

        reordered = subjects + verbs + objects
        words = [b["translated"] for b in reordered if b["translated"]]
        sentence_str = " ".join(words)
        if puncts:
            sentence_str += puncts[-1]["original"]

        if sentence_str:
            sentence_str = sentence_str[0].upper() + sentence_str[1:]

        return {
            "translated_text": sentence_str,
            "breakdown": breakdown
        }

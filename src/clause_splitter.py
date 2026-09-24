import re
from typing import List, Dict, Any, Tuple
from src.utils import turkish_lower


# Clause boundary connectors with preceding comma or strong conjunctions
EN_CLAUSE_CONNECTORS = [
    r",\s+and\b", r",\s+but\b", r",\s+because\b", r",\s+although\b",
    r",\s+while\b", r",\s+whereas\b", r",\s+however\b", r",\s+since\b",
    r",\s+so\b", r",\s+until\b", r",\s+before\b", r",\s+after\b",
    r",\s+(?:the|they|he|she|it|we|you|i|this|that|researchers?|scientists?|people)\b",
    r";\s*", r"\s+--\s+"
]

TR_CLAUSE_CONNECTORS = [
    r",\s+ve\b", r",\s+ama\b", r",\s+fakat\b", r",\s+çünkü\b",
    r",\s+ancak\b", r",\s+oysa\b", r",\s+halbuki\b", r",\s+iken\b",
    r",\s+(?:bu|o|onlar|biz|siz|ben|sen)\b",
    r";\s*", r"\s+--\s+"
]


def split_into_clauses(text: str, lang: str = "auto") -> List[Tuple[str, str]]:
    """
    Splits long or compound sentences into logical clauses while preserving conjunction markers.
    Returns: List of tuples (clause_text, connector_trailing)
    Example:
      'Although he was tired, he finished his work.'
      -> [('Although he was tired', ','), ('he finished his work.', '')]
    """
    text = text.strip()
    if not text:
        return []

    words = text.split()
    # Don't split short or medium sentences (fewer than 9 words)
    if len(words) < 9:
        return [(text, "")]

    connectors = EN_CLAUSE_CONNECTORS if lang == "en" else (TR_CLAUSE_CONNECTORS if lang == "tr" else EN_CLAUSE_CONNECTORS + TR_CLAUSE_CONNECTORS)
    combined_pattern = "(" + "|".join(connectors) + ")"

    splits = re.split(combined_pattern, text, flags=re.IGNORECASE)
    if len(splits) <= 1:
        return [(text, "")]

    clauses = []
    i = 0
    while i < len(splits):
        chunk = splits[i].strip()
        connector = ""
        if i + 1 < len(splits):
            connector = splits[i + 1]
            i += 2
        else:
            i += 1

        if chunk:
            clauses.append((chunk, connector))

    return clauses if clauses else [(text, "")]


def evaluate_confidence(
    input_text: str,
    output_text: str,
    engine: str,
    from_code: str,
    to_code: str,
    breakdown: List[Dict[str, Any]] = None
) -> Tuple[int, str]:
    """
    Computes an empirical Confidence Score (0 - 100%) and confidence level label:
    - 'high' (80-100%): High confidence
    - 'medium' (55-79%): Medium confidence
    - 'low' (<55%): Low confidence / complex sentence warning

    Factors evaluated:
    1. Translation engine baseline (user correction, colloquial idiom, NMT, syntax)
    2. Unknown word count / OOV ratio
    3. Sentence complexity & length penalty
    4. Repetition artifacts
    5. Agreement between syntax breakdown and output
    """
    if engine == "user_correction":
        return 100, "high"

    if engine in ("idiom", "idiom_exact", "idiom_phrase", "slang", "syntax_colloquial"):
        return 96, "high"

    # Baseline by engine
    if engine in ("nmt", "cache"):
        score = 85
    elif engine in ("hybrid", "clause_hybrid"):
        score = 88
    elif engine == "syntax_fallback":
        score = 78
    else:
        score = 75

    in_words = re.findall(r"\b[\w'-]+\b", input_text)
    out_words = re.findall(r"\b[\w'-]+\b", output_text)
    in_len = len(in_words)
    out_len = len(out_words)

    # 1. Repetition loops check in output (e.g. 'the the', 'gitti gitti gitti')
    for i in range(len(out_words) - 1):
        if out_words[i].lower() == out_words[i + 1].lower() and out_words[i].lower() not in ("yavaş", "hızlı", "güzel"):
            score -= 15
            break

    # 2. Length disparity check (e.g., input was 12 words, output is only 2 words)
    if in_len >= 5 and out_len < max(2, in_len // 3):
        score -= 25

    # 3. Sentence complexity penalty for very long convoluted inputs
    if in_len > 22:
        penalty = min(20, int((in_len - 22) * 0.8))
        score -= penalty

    # 4. Unknown tokens in breakdown
    if breakdown:
        unknown_cnt = sum(1 for b in breakdown if b.get("pos") in ("unknown", "unk") or b.get("role") == "unknown")
        if unknown_cnt > 0:
            score -= min(25, unknown_cnt * 7)

        # Verb presence verification
        has_verb = any(b.get("role") in ("verb", "copula_predicate", "copula_negation") for b in breakdown)
        if has_verb and engine in ("nmt", "cache"):
            score += 5  # Bonus for verified finite predicate

    # 5. Verbatim copy check when languages differ
    if from_code != to_code and input_text.strip().lower() == output_text.strip().lower():
        score = min(score, 35)

    # Clamp score
    score = max(20, min(98, score))

    if score >= 80:
        level = "high"
    elif score >= 55:
        level = "medium"
    else:
        level = "low"

    return score, level

"""
Kaikki Turkish Wiktionary Ingestion Pipeline
Downloads and parses 45,949 comprehensive multi-sense entries from Kaikki.org
Extracts:
 - Headwords and clean lemmas
 - Multiple senses with English glosses
 - Parts of speech
 - Register tags (formal, archaic, slang, figurative, medical, etc.)
 - Enriches bilingual table with thousands of high-depth polysemous definitions
"""

import urllib.request
import json
import gzip
import sqlite3
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from src.utils import turkish_lower

DB_PATH = os.path.join(base_dir, "data", "dictionary.db")
URL = "https://kaikki.org/dictionary/Turkish/kaikki.org-dictionary-Turkish.jsonl"

POS_MAP = {
    "noun": "n.",
    "verb": "v.",
    "adj": "adj.",
    "adv": "adv.",
    "pron": "pron.",
    "prep": "prep.",
    "conj": "conj.",
    "intj": "interj.",
    "name": "proper n.",
    "phrase": "phrase",
    "idiom": "idiom"
}

def map_category(tags, pos):
    tags_set = set(tags or [])
    if "idiomatic" in tags_set or "proverb" in tags_set:
        return "Idioms & Proverbs"
    if "slang" in tags_set or "colloquial" in tags_set:
        return "Slang"
    if "formal" in tags_set or "literary" in tags_set or "poetic" in tags_set:
        return "Formal"
    if "archaic" in tags_set or "obsolete" in tags_set:
        return "Archaic"
    if "technical" in tags_set or "medicine" in tags_set or "law" in tags_set or "botany" in tags_set or "zoology" in tags_set:
        return "Technical"
    if "figurative" in tags_set:
        return "Figurative"
    return "Common Usage"

def clean_gloss(gloss):
    if not gloss:
        return ""
    g = gloss.strip()
    # Remove redundant Wiktionary prefixes if any
    if g.startswith("synonym of "):
        g = g.replace("synonym of ", "").split(" (“")[0].strip()
    if g.startswith("ellipsis of "):
        g = g.replace("ellipsis of ", "").split(" (“")[0].strip()
    return g

def analyze_and_ingest(dry_run=True):
    print("=" * 70)
    print(f"KAIKKI TURKISH WIKTIONARY INGESTION (Dry Run: {dry_run})")
    print("=" * 70)

    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'gzip'})
    t0 = time.time()
    print("Downloading stream from Kaikki.org...")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM bilingual;")
    initial_rows = cur.fetchone()[0]
    print(f"Current rows in bilingual: {initial_rows:,}")

    total_lines = 0
    skipped_forms = 0
    candidate_rows = []
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        with gzip.GzipFile(fileobj=resp) as gz:
            for line in gz:
                total_lines += 1
                try:
                    data = json.loads(line.decode('utf-8'))
                except Exception:
                    continue

                word = data.get('word', '').strip()
                pos_raw = data.get('pos', 'noun')
                pos_clean = POS_MAP.get(pos_raw, f"{pos_raw}.")
                senses = data.get('senses', [])
                
                if not word or not senses:
                    continue

                # Skip non-lemma grammatical inflections (e.g., "second-person singular past indicative of...")
                for s in senses:
                    tags = s.get('tags') or []
                    if 'form-of' in tags:
                        skipped_forms += 1
                        continue
                    
                    glosses = s.get('glosses') or []
                    if not glosses:
                        continue
                    
                    primary_gloss = clean_gloss(glosses[0])
                    if not primary_gloss or len(primary_gloss) > 150:
                        continue
                    
                    cat = map_category(tags, pos_raw)
                    tr_low = turkish_lower(word)
                    en_low = primary_gloss.lower()

                    candidate_rows.append((primary_gloss, word, pos_clean, cat, en_low, tr_low))

    print(f"\nStream processed in {time.time()-t0:.1f}s.")
    print(f"Total lines: {total_lines:,}")
    print(f"Skipped inflection forms: {skipped_forms:,}")
    print(f"Extracted valid lemma senses: {len(candidate_rows):,}")

    # Check how many are new vs existing
    new_count = 0
    seen_in_batch = set()
    rows_to_insert = []

    print("\nCross-referencing candidates with current bilingual table...")
    for en, tr, p, cat, en_l, tr_l in candidate_rows:
        key = (tr_l, en_l)
        if key in seen_in_batch:
            continue
        seen_in_batch.add(key)

        cur.execute("SELECT 1 FROM bilingual WHERE tr_lower = ? AND en_lower = ? LIMIT 1;", (tr_l, en_l))
        if not cur.fetchone():
            rows_to_insert.append((en, tr, p, cat, en_l, tr_l))
            new_count += 1

    print(f"New distinct senses to add to dictionary: {new_count:,}")

    if not dry_run and rows_to_insert:
        print(f"\nInserting {len(rows_to_insert):,} rows into bilingual table...")
        cur.executemany("""
            INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower)
            VALUES (?, ?, ?, ?, ?, ?);
        """, rows_to_insert)
        conn.commit()
        print("Done! Database updated.")

    conn.close()

if __name__ == "__main__":
    is_dry = "--commit" not in sys.argv
    analyze_and_ingest(dry_run=is_dry)

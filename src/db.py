import os
import sqlite3
import time
from typing import List, Dict, Any, Optional, Tuple
from src.utils import turkish_lower, get_resource_path

TR_CHARS = set("çğıöşüÇĞİÖŞÜ")

EN_IRREGULAR_LEMMAS = {
    "went": "go", "gone": "go", "goes": "go", "going": "go",
    "saw": "see", "seen": "see", "sees": "see", "seeing": "see",
    "came": "come", "comes": "come", "coming": "come",
    "made": "make", "makes": "make", "making": "make",
    "did": "do", "done": "do", "does": "do", "doing": "do",
    "said": "say", "says": "say", "saying": "say",
    "got": "get", "gotten": "get", "gets": "get", "getting": "get",
    "knew": "know", "known": "know", "knows": "know", "knowing": "know",
    "thought": "think", "thinks": "think", "thinking": "think",
    "took": "take", "taken": "take", "takes": "take", "taking": "take",
    "bought": "buy", "buys": "buy", "buying": "buy",
    "sold": "sell", "sells": "sell", "selling": "sell",
    "found": "find", "finds": "find", "finding": "find",
    "told": "tell", "tells": "tell", "telling": "tell",
    "gave": "give", "given": "give", "gives": "give", "giving": "give",
    "felt": "feel", "feels": "feel", "feeling": "feel",
    "became": "become", "becomes": "become", "becoming": "become",
    "left": "leave", "leaves": "leave", "leaving": "leave",
    "began": "begin", "begun": "begin", "begins": "begin", "beginning": "begin",
    "ran": "run", "runs": "run", "running": "run",
    "wrote": "write", "written": "write", "writes": "write", "writing": "write",
    "sat": "sit", "sits": "sit", "sitting": "sit",
    "stood": "stand", "stands": "stand", "standing": "stand",
    "lost": "lose", "loses": "lose", "losing": "lose",
    "paid": "pay", "pays": "pay", "paying": "pay",
    "met": "meet", "meets": "meet", "meeting": "meet",
    "spoke": "speak", "spoken": "speak", "speaks": "speak", "speaking": "speak",
    "read": "read", "reads": "read", "reading": "read",
    "spent": "spend", "spends": "spend", "spending": "spend",
    "grew": "grow", "grown": "grow", "grows": "grow", "growing": "grow",
    "won": "win", "wins": "win", "winning": "win",
    "taught": "teach", "teaches": "teach", "teaching": "teach",
    "brought": "bring", "brings": "bring", "bringing": "bring",
    "built": "build", "builds": "build", "building": "build",
    "fell": "fall", "fallen": "fall", "falls": "fall", "falling": "fall",
    "better": "good", "best": "good", "worse": "bad", "worst": "bad",
    "children": "child", "people": "person", "men": "man", "women": "woman",
    "feet": "foot", "teeth": "tooth", "mice": "mouse"
}

def get_turkish_candidates(word: str) -> List[str]:
    w = turkish_lower(word)
    candidates = []
    
    verb_suffixes = [
        "dıysam", "diysem", "duysam", "düysem",
        "tıysam", "tiysem", "tuysam", "tüysem",
        "dıysan", "diysen", "duysan", "düysen",
        "tıysan", "tiysen", "tuysan", "tüysen",
        "dıysa", "diyse", "duysa", "düyse",
        "tıysa", "tiyse", "tuysa", "tüyse",
        "mıştım", "miştim", "muştum", "müştüm",
        "acaktım", "ecektim", "acaktın", "ecektin",
        "ıyordum", "iyordum", "uyordum", "üyordum",
        "ıyordun", "iyordun", "uyordun", "üyordun",
        "ıyordu", "iyordu", "uyordu", "üyordu",
        "saydım", "seydim", "saydın", "seydin",
        "dığımda", "diğimde", "duğumda", "düğümde",
        "dıkça", "dikçe", "dukça", "dükçe",
        "dınız", "diniz", "dunuz", "dünüz",
        "tınız", "tiniz", "tunuz", "tünüz",
        "dılar", "diler", "dular", "düler",
        "tılar", "tiler", "tular", "tüler",
        "dık", "dik", "duk", "dük",
        "tık", "tik", "tuk", "tük",
        "dım", "dim", "dum", "düm",
        "tım", "tim", "tum", "tüm",
        "dın", "din", "dun", "dün",
        "tın", "tin", "tun", "tün",
        "dı", "di", "du", "dü",
        "tı", "ti", "tu", "tü",
        "ıyor", "iyor", "uyor", "üyor",
        "acak", "ecek", "miş", "mış", "muş", "müş",
        "ır", "ir", "ur", "ür", "ar", "er"
    ]
    for s in verb_suffixes:
        if w.endswith(s) and len(w) - len(s) >= 2:
            stem = w[:-len(s)]
            candidates.append(stem + "mek")
            candidates.append(stem + "mak")
            candidates.append(stem)

    noun_suffixes = [
        "lardan", "lerden", "larda", "lerde", "lara", "lere", "ları", "leri", "ların", "lerin",
        "ımızdan", "imizden", "umuzdan", "ümüzden",
        "ınızdan", "inizden", "unuzdan", "ünüzden",
        "ımdan", "imden", "umdan", "ümden",
        "ından", "inden", "undan", "ünden",
        "ımızda", "imizde", "umuzda", "ümüzde",
        "ınızda", "inizde", "unuzda", "ünüzde",
        "ımda", "imde", "umda", "ümde",
        "ında", "inde", "unda", "ünde",
        "dan", "den", "tan", "ten",
        "da", "de", "ta", "te",
        "lar", "ler", "nın", "nin", "nun", "nün",
        "ya", "ye", "na", "ne", "a", "e",
        "yı", "yi", "yu", "yü", "nı", "ni", "nu", "nü", "ı", "i", "u", "ü"
    ]
    for s in noun_suffixes:
        if w.endswith(s) and len(w) - len(s) >= 2:
            stem = w[:-len(s)]
            candidates.append(stem)
            if stem.endswith("b"): candidates.append(stem[:-1] + "p")
            elif stem.endswith("c"): candidates.append(stem[:-1] + "ç")
            elif stem.endswith("d"): candidates.append(stem[:-1] + "t")
            elif stem.endswith("ğ"): candidates.append(stem[:-1] + "k")

    return list(dict.fromkeys(candidates))

def get_english_candidates(word: str) -> List[str]:
    w = word.lower().strip()
    candidates = []
    if w in EN_IRREGULAR_LEMMAS:
        candidates.append(EN_IRREGULAR_LEMMAS[w])
    
    if w.endswith("ies") and len(w) > 4:
        candidates.append(w[:-3] + "y")
    if w.endswith("es") and len(w) > 3:
        candidates.append(w[:-2])
    if w.endswith("s") and len(w) > 2:
        candidates.append(w[:-1])
    if w.endswith("ed") and len(w) > 3:
        candidates.append(w[:-2])
        candidates.append(w[:-1])
    if w.endswith("ing") and len(w) > 4:
        candidates.append(w[:-3])
        candidates.append(w[:-3] + "e")
        if len(w) >= 6 and w[-4] == w[-5]:
            candidates.append(w[:-4])
    if w.endswith("er") and len(w) > 3:
        candidates.append(w[:-2])
        candidates.append(w[:-1])
    if w.endswith("est") and len(w) > 4:
        candidates.append(w[:-3])
        candidates.append(w[:-2])
    if w.endswith("ly") and len(w) > 3:
        candidates.append(w[:-2])
        candidates.append(w[:-2] + "le")

    return list(dict.fromkeys(candidates))

class DictionaryDB:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = get_resource_path(os.path.join("data", "dictionary.db"))
        
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Veritabanı dosyası bulunamadı: {self.db_path}")

        # Connect to SQLite
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cur = self.conn.cursor()
        
        # High-performance read-only pragmas
        self.cur.execute("PRAGMA query_only = ON;")
        self.cur.execute("PRAGMA cache_size = 50000;")
        self.cur.execute("PRAGMA mmap_size = 268435456;") # 256MB memory map
        self.cur.execute("PRAGMA synchronous = OFF;")

    def detect_language(self, query: str) -> str:
        """Detect if input query is more likely Turkish or English."""
        # 1. Distinctive Turkish letters
        if any(c in TR_CHARS for c in query):
            return "tr"

        q_lower = turkish_lower(query)

        # 2. Check bilingual exact hit comparison
        self.cur.execute("SELECT COUNT(*) FROM bilingual WHERE tr_lower = ?;", (q_lower,))
        tr_exact = self.cur.fetchone()[0]
        self.cur.execute("SELECT COUNT(*) FROM bilingual WHERE en_lower = ?;", (q_lower,))
        en_exact = self.cur.fetchone()[0]

        if en_exact > 0 and tr_exact == 0:
            return "en"
        if tr_exact > 0 and en_exact == 0:
            return "tr"
        if en_exact > 0 and tr_exact > 0:
            return "en" if en_exact >= tr_exact else "tr"

        # 3. Check official monolingual dictionaries (TDK vs Webster)
        self.cur.execute("SELECT 1 FROM tr_definitions WHERE word_lower = ? LIMIT 1;", (q_lower,))
        if self.cur.fetchone():
            return "tr"

        self.cur.execute("SELECT 1 FROM en_definitions WHERE word_lower = ? LIMIT 1;", (q_lower,))
        if self.cur.fetchone():
            return "en"

        # 4. Check prefix hits comparison
        upper = q_lower + "\uffff"
        self.cur.execute("SELECT COUNT(*) FROM (SELECT 1 FROM bilingual WHERE tr_lower >= ? AND tr_lower < ? LIMIT 6);", (q_lower, upper))
        tr_cnt = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM (SELECT 1 FROM bilingual WHERE en_lower >= ? AND en_lower < ? LIMIT 6);", (q_lower, upper))
        en_cnt = self.cur.fetchone()[0]

        if tr_cnt > en_cnt:
            return "tr"
        if en_cnt > tr_cnt:
            return "en"

        # Default fallback to English
        return "en"

    def search(self, query: str, mode: str = "auto", limit: int = 100, show_slang_profanity: bool = True) -> Tuple[List[Dict[str, Any]], float, str]:
        """
        Search dictionary with sub-millisecond range/exact query, morphological root fallback,
        and official TDK / Webster definition fallback.
        Supports filtering out slang and profanity ('Argo / Sokak Dili') when show_slang_profanity=False.
        Returns: (results_list, elapsed_ms, detected_direction)
        """
        query = query.strip()
        if not query:
            return [], 0.0, ""

        t_start = time.perf_counter()
        q_lower = turkish_lower(query)

        # Determine search direction
        direction = mode
        if mode == "auto":
            lang = self.detect_language(query)
            direction = "en_tr" if lang == "en" else "tr_en"

        is_en = (direction == "en_tr")
        src_col = "en_lower" if is_en else "tr_lower"
        upper_bound = q_lower + "\uffff"

        slang_filter = "" if show_slang_profanity else "AND category NOT IN ('Argo / Sokak Dili', 'Slang', 'Argo')"

        # Query using B-Tree range & exact matching with prioritized sorting
        sql = f"""
        SELECT en, tr, type, category, {src_col}
        FROM bilingual
        WHERE {src_col} >= ? AND {src_col} < ? {slang_filter}
        ORDER BY 
            CASE WHEN {src_col} = ? THEN 0 ELSE 1 END,
            CASE 
                WHEN category = 'Primary' THEN -3
                WHEN category = 'Idioms & Proverbs' THEN -2
                WHEN category = 'Common Usage' THEN -1
                WHEN category = 'CEFR A1' THEN 0
                WHEN category = 'CEFR A2' THEN 1
                WHEN category = 'CEFR B1' THEN 2
                WHEN category = 'CEFR B2' THEN 3
                WHEN category = 'CEFR C1' THEN 4
                WHEN category = 'CEFR C2' THEN 5
                WHEN category LIKE 'CEFR%' THEN 5
                WHEN category = 'Formal' THEN 6
                WHEN category = 'Temel Çekim' THEN 7
                WHEN category = 'İngilizce Düzensiz Fiil' THEN 8
                WHEN category = 'İngilizce Derecelendirme' THEN 9
                WHEN category = 'İngilizce Düzensiz Çoğul' THEN 10
                WHEN category = 'TDK Atasözleri ve Deyimler' THEN 11
                WHEN category = 'Idioms' THEN 11
                WHEN category = 'Proverb' THEN 11
                WHEN category = 'Wiktionary' THEN 12
                WHEN category = 'Wiktionary / Çekim' THEN 13
                WHEN category = 'FreeDict' THEN 14
                WHEN category = 'General' THEN 15
                ELSE 16
            END,
            length({src_col}) ASC
        LIMIT ?;
        """

        self.cur.execute(sql, (q_lower, upper_bound, q_lower, limit))
        raw_rows = self.cur.fetchall()

        # If no results and mode was auto, try the other direction
        if not raw_rows and mode == "auto":
            alt_is_en = not is_en
            alt_src_col = "en_lower" if alt_is_en else "tr_lower"
            alt_sql = f"""
            SELECT en, tr, type, category, {alt_src_col}
            FROM bilingual
            WHERE {alt_src_col} >= ? AND {alt_src_col} < ? {slang_filter}
            ORDER BY 
                CASE WHEN {alt_src_col} = ? THEN 0 ELSE 1 END,
                CASE 
                    WHEN category = 'Primary' THEN -3
                    WHEN category = 'Idioms & Proverbs' THEN -2
                    WHEN category = 'Common Usage' THEN -1
                    WHEN category = 'CEFR A1' THEN 0
                    WHEN category = 'CEFR A2' THEN 1
                    WHEN category = 'CEFR B1' THEN 2
                    WHEN category = 'CEFR B2' THEN 3
                    WHEN category = 'CEFR C1' THEN 4
                    WHEN category = 'CEFR C2' THEN 5
                    WHEN category LIKE 'CEFR%' THEN 5
                    WHEN category = 'Formal' THEN 6
                    WHEN category = 'Temel Çekim' THEN 7
                    WHEN category = 'İngilizce Düzensiz Fiil' THEN 8
                    WHEN category = 'İngilizce Derecelendirme' THEN 9
                    WHEN category = 'İngilizce Düzensiz Çoğul' THEN 10
                    WHEN category = 'TDK Atasözleri ve Deyimler' THEN 11
                    WHEN category = 'Idioms' THEN 11
                    WHEN category = 'Proverb' THEN 11
                    WHEN category = 'Wiktionary' THEN 12
                    WHEN category = 'Wiktionary / Çekim' THEN 13
                    WHEN category = 'FreeDict' THEN 14
                    WHEN category = 'General' THEN 15
                    ELSE 16
                END,
                length({alt_src_col}) ASC
            LIMIT ?;
            """
            self.cur.execute(alt_sql, (q_lower, upper_bound, q_lower, limit))
            alt_rows = self.cur.fetchall()
            if alt_rows:
                raw_rows = alt_rows
                is_en = alt_is_en
                direction = "en_tr" if is_en else "tr_en"
                src_col = alt_src_col

        results = []
        for row in raw_rows:
            results.append({
                "source": row[0] if is_en else row[1],
                "target": row[1] if is_en else row[0],
                "type": row[2] or "-",
                "category": row[3] or "General",
                "direction": "EN ➔ TR" if is_en else "TR ➔ EN"
            })

        # -------------------------------------------------------------
        # MORPHOLOGICAL ROOT/LEMMA FALLBACK (if 0 or very few results)
        # -------------------------------------------------------------
        if len(results) == 0:
            if not is_en:
                # Turkish morphology fallback
                candidates = get_turkish_candidates(query)
                for cand in candidates:
                    cand_upper = cand + "\uffff"
                    self.cur.execute(sql, (cand, cand_upper, cand, 10))
                    c_rows = self.cur.fetchall()
                    if c_rows:
                        for row in c_rows:
                            results.append({
                                "source": f"{query} (Kök: {cand})",
                                "target": row[0],
                                "type": f"{row[2] or '-'} (kök türevi)",
                                "category": "Morfolojik Analiz",
                                "direction": "TR ➔ EN"
                            })
                        break
            else:
                # English morphology fallback
                candidates = get_english_candidates(query)
                for cand in candidates:
                    cand_upper = cand + "\uffff"
                    self.cur.execute(sql, (cand, cand_upper, cand, 10))
                    c_rows = self.cur.fetchall()
                    if c_rows:
                        for row in c_rows:
                            results.append({
                                "source": f"{query} (Root: {cand})",
                                "target": row[1],
                                "type": f"{row[2] or '-'} (lemma)",
                                "category": "Morphological Analysis",
                                "direction": "EN ➔ TR"
                            })
                        break

        # -------------------------------------------------------------
        # MONOLINGUAL DEFINITION FALLBACK (TDK / Webster)
        # -------------------------------------------------------------
        if len(results) == 0:
            # Check TDK
            tdk_defs = self.get_tr_definitions(query)
            if tdk_defs:
                for d in tdk_defs[:5]:
                    results.append({
                        "source": query,
                        "target": d["meaning"],
                        "type": "TDK Tanım",
                        "category": "TDK Güncel Sözlük",
                        "direction": "TR (Tanım)"
                    })
            else:
                # Check Webster
                webster_def = self.get_en_definition(query)
                if webster_def:
                    results.append({
                        "source": query,
                        "target": webster_def,
                        "type": "Webster Def",
                        "category": "Webster's Dictionary",
                        "direction": "EN (Definition)"
                    })

        elapsed_ms = (time.perf_counter() - t_start) * 1000
        return results, elapsed_ms, "EN ➔ TR" if is_en else "TR ➔ EN"

    def get_tr_definitions(self, word: str) -> List[Dict[str, Optional[str]]]:
        """Fetch official TDK Turkish definitions, examples, and authors."""
        w_lower = turkish_lower(word.strip())
        self.cur.execute("""
        SELECT meaning, example, author 
        FROM tr_definitions 
        WHERE word_lower = ? 
        LIMIT 10;
        """, (w_lower,))
        rows = self.cur.fetchall()
        return [{"meaning": r[0], "example": r[1], "author": r[2]} for r in rows]

    def get_en_definition(self, word: str) -> Optional[str]:
        """Fetch Webster's English definition."""
        w_lower = word.strip().lower()
        self.cur.execute("""
        SELECT definition 
        FROM en_definitions 
        WHERE word_lower = ? 
        LIMIT 1;
        """, (w_lower,))
        row = self.cur.fetchone()
        return row[0] if row else None

    def close(self):
        if self.conn:
            self.conn.close()

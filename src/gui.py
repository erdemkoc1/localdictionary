import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Optional
from src.db import DictionaryDB
from src.history import HistoryManager
from src.syntax_engine import SyntaxTranslator

class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent, history_manager: HistoryManager, on_select_callback):
        super().__init__(parent)
        self.parent = parent
        self.history_manager = history_manager
        self.on_select_callback = on_select_callback

        self.title("Arama Geçmişi")
        self.geometry("560x420")
        self.minsize(450, 300)
        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=16, pady=(14, 8))

        lbl = ctk.CTkLabel(top_frame, text="🕒 Arama Geçmişi", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(side="left")

        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(fill="both", expand=True, padx=16, pady=0)

        columns = ("query", "direction", "time")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("query", text="Aranan Kelime / İfade")
        self.tree.heading("direction", text="Yön")
        self.tree.heading("time", text="Son Arama Tarihi")

        self.tree.column("query", width=220)
        self.tree.column("direction", width=90, anchor="center")
        self.tree.column("time", width=180, anchor="center")

        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self.search_selected())

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=12)

        self.search_btn = ctk.CTkButton(
            btn_frame, 
            text="Seçileni Ara", 
            width=110,
            command=self.search_selected
        )
        self.search_btn.pack(side="left", padx=(0, 8))

        self.delete_btn = ctk.CTkButton(
            btn_frame, 
            text="Sil", 
            width=80,
            fg_color=("gray75", "gray35"),
            hover_color=("gray65", "gray45"),
            command=self.delete_selected
        )
        self.delete_btn.pack(side="left", padx=(0, 8))

        self.clear_btn = ctk.CTkButton(
            btn_frame, 
            text="Tümünü Temizle", 
            width=120,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            command=self.clear_all
        )
        self.clear_btn.pack(side="right")

    def load_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        items = self.history_manager.get_recent(limit=100)
        for it in items:
            self.tree.insert("", "end", values=(it["query"], it["direction"], it.get("search_time", "-")))

    def search_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        if values:
            query = values[0]
            self.on_select_callback(query)
            self.destroy()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        if values:
            query = values[0]
            self.history_manager.delete_search(query)
            self.load_history()
            self.parent.update_quick_history()

    def clear_all(self):
        if messagebox.askyesno("Geçmişi Temizle", "Tüm arama geçmişiniz kalıcı olarak silinecek. Onaylıyor musunuz?", parent=self):
            self.history_manager.clear_all()
            self.load_history()
            self.parent.update_quick_history()


class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window settings
        self.title("LocalDictionary (TR ⇄ EN) - Portable")
        self.geometry("1040x740")
        self.minsize(840, 580)

        # Initialize Database, History, and Syntax Engine
        try:
            self.db = DictionaryDB()
        except Exception as e:
            self.show_fatal_error(str(e))
            return

        self.history = HistoryManager()
        self.syntax_translator = SyntaxTranslator()
        self.history_window: Optional[HistoryWindow] = None

        # State
        self.current_theme = "dark"
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.debounce_timer: Optional[str] = None
        self.current_results = []

        # Setup GUI Components
        self.setup_ui()
        self.apply_treeview_theme()
        self.update_quick_history()

        # Initial search hint
        self.search_entry.focus()
        self.perform_search("welcome", save_to_history=False)

    def show_fatal_error(self, msg: str):
        lbl = ctk.CTkLabel(self, text=f"Hata: {msg}", text_color="red", font=("Arial", 16))
        lbl.pack(expand=True, padx=20, pady=20)

    def setup_ui(self):
        # 1. Top Header Frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, height=55)
        self.header_frame.pack(fill="x", padx=0, pady=0)
        self.header_frame.pack_propagate(False)

        # App Title & Subtitle
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="LOCALDICTIONARY", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(side="left", padx=(18, 5), pady=12)

        self.sub_label = ctk.CTkLabel(
            self.header_frame, 
            text="v1.3 (100% Çevrimdışı)", 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.sub_label.pack(side="left", padx=0, pady=(15, 12))

        # Theme Switch Button
        self.theme_btn = ctk.CTkButton(
            self.header_frame, 
            text="☀️ Açık Tema", 
            width=95,
            height=30,
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="right", padx=16, pady=12)

        # History Button
        self.history_btn = ctk.CTkButton(
            self.header_frame,
            text="🕒 Geçmiş",
            width=85,
            height=30,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=self.open_history_window
        )
        self.history_btn.pack(side="right", padx=(0, 10), pady=12)

        # 2. Main Tabview (Sözlük vs Cümle Çevirisi)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=(4, 0))

        self.tab_dict = self.tabview.add("🔍 Sözlük / Kelime Arama")
        self.tab_sentence = self.tabview.add("⚡ Cümle & Sentaks Çevirisi (BETA)")

        self.setup_dictionary_tab()
        self.setup_sentence_tab()

        # 5. Bottom Status Bar
        self.status_bar = ctk.CTkFrame(self, height=32, corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)

        self.status_left = ctk.CTkLabel(
            self.status_bar, 
            text="Hazır", 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_left.pack(side="left", padx=18)

        self.status_right = ctk.CTkLabel(
            self.status_bar, 
            text="● 2.2M+ Sözlük & Sentaks Motoru (100% Çevrimdışı)", 
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50"
        )
        self.status_right.pack(side="right", padx=18)

    # ---------------- TAB 1: DICTIONARY ----------------
    def setup_dictionary_tab(self):
        dir_frame = ctk.CTkFrame(self.tab_dict, fg_color="transparent")
        dir_frame.pack(fill="x", padx=4, pady=(2, 6))

        dir_lbl = ctk.CTkLabel(dir_frame, text="Arama Yönü:", font=ctk.CTkFont(size=12), text_color="gray")
        dir_lbl.pack(side="left", padx=(0, 8))

        self.dir_selector = ctk.CTkSegmentedButton(
            dir_frame,
            values=["Otomatik", "EN ➔ TR", "TR ➔ EN"],
            command=lambda val: self.on_search_change()
        )
        self.dir_selector.set("Otomatik")
        self.dir_selector.pack(side="left")

        # Search box frame
        self.search_frame = ctk.CTkFrame(self.tab_dict, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=4, pady=(2, 2))

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Kelime veya deyim yazın... (Örn: computer, başarı, serendipity, break)",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", self.on_key_release)
        self.search_entry.bind("<Return>", lambda e: self.perform_search(self.search_entry.get()))

        self.clear_btn = ctk.CTkButton(
            self.search_frame,
            text="✕",
            width=38,
            height=40,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=self.clear_search
        )
        self.clear_btn.pack(side="left", padx=(0, 8))

        self.search_btn = ctk.CTkButton(
            self.search_frame,
            text="Ara",
            width=75,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self.perform_search(self.search_entry.get())
        )
        self.search_btn.pack(side="left")

        # Quick History Chips Frame
        self.quick_history_frame = ctk.CTkFrame(self.tab_dict, fg_color="transparent", height=26)
        self.quick_history_frame.pack(fill="x", padx=4, pady=(2, 6))
        self.quick_history_frame.pack_propagate(False)

        # Content Frame
        self.content_frame = ctk.CTkFrame(self.tab_dict, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=4, pady=0)

        # Treeview for results
        self.tree_frame = ctk.CTkFrame(self.content_frame)
        self.tree_frame.pack(fill="both", expand=True, pady=(0, 8))

        columns = ("source", "type", "category", "target")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("source", text="Kaynak Kelime / İfade")
        self.tree.heading("type", text="Tür")
        self.tree.heading("category", text="Kategori")
        self.tree.heading("target", text="Çeviri / Karşılık")

        self.tree.column("source", width=220, minwidth=140)
        self.tree.column("type", width=70, minwidth=60, anchor="center")
        self.tree.column("category", width=140, minwidth=100)
        self.tree.column("target", width=420, minwidth=200)

        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_row_selected)
        self.tree.bind("<Double-1>", self.copy_selected_translation)

        # Detail / Definition Box
        self.detail_frame = ctk.CTkFrame(self.content_frame, height=130)
        self.detail_frame.pack(fill="x", pady=(0, 4))
        self.detail_frame.pack_propagate(False)

        self.detail_header = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        self.detail_header.pack(fill="x", padx=10, pady=(4, 2))

        self.detail_title = ctk.CTkLabel(
            self.detail_header, 
            text="Sözlük Tanımı & Bilgi", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.detail_title.pack(side="left")

        self.copy_btn = ctk.CTkButton(
            self.detail_header,
            text="Çeviriyi Kopyala",
            width=110,
            height=24,
            font=ctk.CTkFont(size=11),
            command=self.copy_selected_translation
        )
        self.copy_btn.pack(side="right")

        self.detail_text = ctk.CTkTextbox(
            self.detail_frame, 
            wrap="word", 
            font=ctk.CTkFont(size=12),
            activate_scrollbars=True
        )
        self.detail_text.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        self.detail_text.configure(state="disabled")

    # ---------------- TAB 2: SENTENCE & SYNTAX TRANSLATION (BETA) ----------------
    def setup_sentence_tab(self):
        # Options row
        opt_frame = ctk.CTkFrame(self.tab_sentence, fg_color="transparent")
        opt_frame.pack(fill="x", padx=6, pady=(4, 6))

        lbl = ctk.CTkLabel(opt_frame, text="Çeviri Yönü:", font=ctk.CTkFont(size=12), text_color="gray")
        lbl.pack(side="left", padx=(0, 8))

        self.sent_dir_selector = ctk.CTkSegmentedButton(
            opt_frame,
            values=["Otomatik Algıla", "İngilizce ➔ Türkçe", "Türkçe ➔ İngilizce"]
        )
        self.sent_dir_selector.set("Otomatik Algıla")
        self.sent_dir_selector.pack(side="left")

        # Source input section
        src_lbl_frame = ctk.CTkFrame(self.tab_sentence, fg_color="transparent")
        src_lbl_frame.pack(fill="x", padx=6, pady=(2, 2))

        ctk.CTkLabel(src_lbl_frame, text="Çevrilecek Cümle / Metin:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

        self.sent_input = ctk.CTkTextbox(self.tab_sentence, height=75, font=ctk.CTkFont(size=13), wrap="word")
        self.sent_input.pack(fill="x", padx=6, pady=(0, 6))

        # Action buttons
        btn_frame = ctk.CTkFrame(self.tab_sentence, fg_color="transparent")
        btn_frame.pack(fill="x", padx=6, pady=(0, 6))

        self.translate_action_btn = ctk.CTkButton(
            btn_frame,
            text="⚡ Çevir (Sentaks & Sözlük Motoru)",
            width=220,
            height=32,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.start_sentence_translation
        )
        self.translate_action_btn.pack(side="left", padx=(0, 8))

        self.sent_clear_btn = ctk.CTkButton(
            btn_frame,
            text="✕ Temizle",
            width=85,
            height=32,
            fg_color=("gray75", "gray35"),
            hover_color=("gray65", "gray45"),
            command=self.clear_sentence_inputs
        )
        self.sent_clear_btn.pack(side="left")

        self.sent_loading_lbl = ctk.CTkLabel(
            btn_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#3B8ED0"
        )
        self.sent_loading_lbl.pack(side="left", padx=12)

        # Target output section
        tgt_lbl_frame = ctk.CTkFrame(self.tab_sentence, fg_color="transparent")
        tgt_lbl_frame.pack(fill="x", padx=6, pady=(2, 2))

        ctk.CTkLabel(tgt_lbl_frame, text="Sentaks Düzeltilmiş Çeviri Sonucu:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

        self.sent_copy_btn = ctk.CTkButton(
            tgt_lbl_frame,
            text="Sonucu Kopyala",
            width=110,
            height=24,
            font=ctk.CTkFont(size=11),
            command=self.copy_sentence_result
        )
        self.sent_copy_btn.pack(side="right")

        self.sent_output = ctk.CTkTextbox(self.tab_sentence, height=70, font=ctk.CTkFont(size=13, weight="bold"), wrap="word")
        self.sent_output.pack(fill="x", padx=6, pady=(0, 6))
        self.sent_output.configure(state="disabled")

        # Breakdown section (Interlinear table)
        breakdown_lbl_frame = ctk.CTkFrame(self.tab_sentence, fg_color="transparent")
        breakdown_lbl_frame.pack(fill="x", padx=6, pady=(2, 2))

        ctk.CTkLabel(breakdown_lbl_frame, text="📊 Kelime ve Kalıp Analizi (Sözlük & Gramer Rolleri):", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")

        self.breakdown_frame = ctk.CTkFrame(self.tab_sentence)
        self.breakdown_frame.pack(fill="both", expand=True, padx=6, pady=(0, 4))

        b_cols = ("original", "role", "pos", "translated", "alts")
        self.breakdown_tree = ttk.Treeview(self.breakdown_frame, columns=b_cols, show="headings", selectmode="browse")
        
        self.breakdown_tree.heading("original", text="Orijinal Sözcük / Kalıp")
        self.breakdown_tree.heading("role", text="Gramer Rolü")
        self.breakdown_tree.heading("pos", text="Kelime Türü")
        self.breakdown_tree.heading("translated", text="Seçilen Çeviri")
        self.breakdown_tree.heading("alts", text="Alternatif Anlamlar")

        self.breakdown_tree.column("original", width=160)
        self.breakdown_tree.column("role", width=110, anchor="center")
        self.breakdown_tree.column("pos", width=90, anchor="center")
        self.breakdown_tree.column("translated", width=180)
        self.breakdown_tree.column("alts", width=250)

        b_scroll = ttk.Scrollbar(self.breakdown_frame, orient="vertical", command=self.breakdown_tree.yview)
        self.breakdown_tree.configure(yscrollcommand=b_scroll.set)
        
        self.breakdown_tree.pack(side="left", fill="both", expand=True)
        b_scroll.pack(side="right", fill="y")

    def clear_sentence_inputs(self):
        """Completely clears input, output, breakdown, and resets status."""
        self.sent_input.delete("0.0", "end")
        self.sent_input.delete("1.0", "end")
        
        self.sent_output.configure(state="normal")
        self.sent_output.delete("0.0", "end")
        self.sent_output.delete("1.0", "end")
        self.sent_output.configure(state="disabled")

        for item in self.breakdown_tree.get_children():
            self.breakdown_tree.delete(item)

        self.sent_loading_lbl.configure(text="")
        self.status_left.configure(text="Cümle çevirisi temizlendi.")
        self.sent_input.focus()

    def copy_sentence_result(self):
        content = self.sent_output.get("1.0", "end").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            old_text = self.sent_copy_btn.cget("text")
            self.sent_copy_btn.configure(text="Kopyalandı! ✓")
            self.after(1500, lambda: self.sent_copy_btn.configure(text=old_text))

    def start_sentence_translation(self):
        text = self.sent_input.get("1.0", "end").strip()
        if not text:
            return

        choice = self.sent_dir_selector.get()
        if choice == "İngilizce ➔ Türkçe":
            dir_code = "en_tr"
        elif choice == "Türkçe ➔ İngilizce":
            dir_code = "tr_en"
        else:
            dir_code = "auto"

        # Execute instant syntax translation (sub-millisecond)
        res = self.syntax_translator.translate(text, direction=dir_code)
        
        # Display translated sentence
        self.sent_output.configure(state="normal")
        self.sent_output.delete("0.0", "end")
        self.sent_output.delete("1.0", "end")
        self.sent_output.insert("0.0", res["translated_text"])
        self.sent_output.configure(state="disabled")

        # Populate breakdown table
        for item in self.breakdown_tree.get_children():
            self.breakdown_tree.delete(item)

        for b in res.get("breakdown", []):
            alts_str = ", ".join(b.get("alternatives", []))
            self.breakdown_tree.insert("", "end", values=(
                b.get("original", ""),
                b.get("role", ""),
                b.get("pos", ""),
                b.get("translated", ""),
                alts_str
            ))

        self.sent_loading_lbl.configure(text="✓ Çeviri Tamamlandı")
        self.status_left.configure(text="Cümle & Sentaks çevirisi tamamlandı.")

    # ---------------- UTILITY / THEME / COMMON ----------------
    def update_quick_history(self):
        for child in self.quick_history_frame.winfo_children():
            child.destroy()

        recent = self.history.get_recent(limit=6)
        if not recent:
            return

        lbl = ctk.CTkLabel(
            self.quick_history_frame, 
            text="Son Aramalar:", 
            font=ctk.CTkFont(size=11), 
            text_color="gray"
        )
        lbl.pack(side="left", padx=(0, 6))

        for r in recent:
            q = r["query"]
            btn = ctk.CTkButton(
                self.quick_history_frame,
                text=q,
                height=22,
                font=ctk.CTkFont(size=11),
                fg_color=("gray85", "gray25"),
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35"),
                command=lambda word=q: self.quick_search(word)
            )
            btn.pack(side="left", padx=3)

    def quick_search(self, word: str):
        self.tabview.set("🔍 Sözlük / Kelime Arama")
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, word)
        self.perform_search(word)

    def open_history_window(self):
        if self.history_window is None or not self.history_window.winfo_exists():
            self.history_window = HistoryWindow(self, self.history, self.quick_search)
        else:
            self.history_window.focus()

    def apply_treeview_theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        if self.current_theme == "dark":
            bg = "#2b2b2b"
            fg = "#f0f0f0"
            field_bg = "#2b2b2b"
            heading_bg = "#1f1f1f"
            heading_fg = "#ffffff"
            sel_bg = "#1f538d"
            sel_fg = "#ffffff"
        else:
            bg = "#ffffff"
            fg = "#1a1a1a"
            field_bg = "#ffffff"
            heading_bg = "#e5e5e5"
            heading_fg = "#1a1a1a"
            sel_bg = "#3b8ed0"
            sel_fg = "#ffffff"

        for tv_name in ["Treeview"]:
            style.configure(
                tv_name,
                background=bg,
                foreground=fg,
                fieldbackground=field_bg,
                rowheight=26,
                font=("Segoe UI", 10),
                borderwidth=0
            )
            style.map(tv_name, background=[("selected", sel_bg)], foreground=[("selected", sel_fg)])
            
            style.configure(
                f"{tv_name}.Heading",
                background=heading_bg,
                foreground=heading_fg,
                font=("Segoe UI", 10, "bold"),
                relief="flat",
                padding=4
            )
            style.map(f"{tv_name}.Heading", background=[("active", heading_bg)])

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="🌙 Koyu Tema")
        else:
            self.current_theme = "dark"
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="☀️ Açık Tema")
        
        self.apply_treeview_theme()

    def on_key_release(self, event):
        if event.keysym in ("Up", "Down", "Left", "Right", "Return", "Escape", "Control_L", "Control_R"):
            return
        
        if self.debounce_timer:
            self.after_cancel(self.debounce_timer)
        
        self.debounce_timer = self.after(180, self.on_search_change)

    def on_search_change(self):
        text = self.search_entry.get().strip()
        self.perform_search(text)

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.search_entry.focus()
        self.clear_results()
        self.status_left.configure(text="Arama temizlendi.")

    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.current_results.clear()
        self.set_detail_text("")

    def perform_search(self, query: str, save_to_history: bool = True):
        query = query.strip()
        if not query:
            self.clear_results()
            return

        sel_mode = self.dir_selector.get()
        mode_map = {
            "Otomatik": "auto",
            "EN ➔ TR": "en_tr",
            "TR ➔ EN": "tr_en"
        }
        mode = mode_map.get(sel_mode, "auto")

        results, elapsed_ms, detected_dir = self.db.search(query, mode=mode, limit=100)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.current_results = results
        for r in results:
            self.tree.insert("", "end", values=(r["source"], r["type"], r["category"], r["target"]))

        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self.on_row_selected(None)
            
            if save_to_history and len(query) >= 2:
                self.history.add_search(query, detected_dir, len(results))
                self.update_quick_history()
        else:
            self.show_no_results(query)

        self.status_left.configure(text=f"{len(results)} sonuç bulundu ({elapsed_ms:.1f} ms) — Yön: {detected_dir}")

    def show_no_results(self, query: str):
        self.set_detail_text(f"'{query}' kelimesi için doğrudan eşleşme bulunamadı.\n\nİpucu: Yazımı kontrol edebilir veya üstteki '⚡ Cümle & Sentaks Çevirisi (BETA)' sekmesinden cümle çevirisini deneyebilirsiniz.")

    def on_row_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0], "values")
        if not values:
            return

        source, wtype, category, target = values
        detail_lines = [f"【{source}】 ➔ {target} ({wtype} - {category})", ""]
        
        tdk_defs = self.db.get_tr_definitions(source)
        if not tdk_defs:
            tdk_defs = self.db.get_tr_definitions(target)

        if tdk_defs:
            detail_lines.append("📖 TDK Güncel Türkçe Sözlük Tanımı:")
            for i, d in enumerate(tdk_defs[:3], 1):
                detail_lines.append(f"  {i}. {d['meaning']}")
                if d.get("example"):
                    author = f" ({d['author']})" if d.get("author") else ""
                    detail_lines.append(f"     \"{d['example']}\"{author}")
            detail_lines.append("")

        webster_def = self.db.get_en_definition(source)
        if not webster_def:
            webster_def = self.db.get_en_definition(target)

        if webster_def:
            detail_lines.append("📘 Webster's English Dictionary:")
            detail_lines.append(f"  {webster_def.strip()}")

        if not tdk_defs and not webster_def:
            detail_lines.append("Detaylı sözlük açıklaması bulunamadı; çeviri karşılıkları yukarıdaki listede yer almaktadır.")

        self.set_detail_text("\n".join(detail_lines))

    def set_detail_text(self, text: str):
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", text)
        self.detail_text.configure(state="disabled")

    def copy_selected_translation(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0], "values")
        if values:
            target = values[3]
            self.clipboard_clear()
            self.clipboard_append(target)
            old_status = self.status_left.cget("text")
            self.status_left.configure(text=f"Kopyalandı: '{target}'")
            self.after(1500, lambda: self.status_left.configure(text=old_status))

    def destroy(self):
        if hasattr(self, "db") and self.db:
            self.db.close()
        if hasattr(self, "syntax_translator") and self.syntax_translator:
            if hasattr(self.syntax_translator, "conn") and self.syntax_translator.conn:
                self.syntax_translator.conn.close()
        super().destroy()

def run_app():
    app = TranslatorApp()
    app.mainloop()

if __name__ == "__main__":
    run_app()

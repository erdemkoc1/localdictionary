import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Optional, List, Dict, Any

from src.db import DictionaryDB
from src.history import HistoryManager
from src.syntax_engine import SyntaxTranslator
from src.settings import SettingsManager
from src.quick_translate import QuickTranslatePopup, GlobalQuickTranslateService, attach_context_menu


class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent, history_manager: HistoryManager, on_select_callback, settings_mgr: SettingsManager):
        super().__init__(parent)
        self.parent = parent
        self.history_manager = history_manager
        self.on_select_callback = on_select_callback
        self.settings = settings_mgr

        self.title(self.settings.get_text("history_btn"))
        self.geometry("580x430")
        self.minsize(460, 320)
        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.load_history()

    def gt(self, key: str) -> str:
        return self.settings.get_text(key)

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=16, pady=(14, 8))

        lbl = ctk.CTkLabel(top_frame, text=self.gt("history_btn"), font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(side="left")

        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(fill="both", expand=True, padx=16, pady=0)

        columns = ("query", "direction", "time")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("query", text=self.gt("col_source"))
        self.tree.heading("direction", text=self.gt("search_dir_lbl"))
        self.tree.heading("time", text="Tarih / Time")

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
            text=self.gt("search_btn"), 
            width=110,
            command=self.search_selected
        )
        self.search_btn.pack(side="left", padx=(0, 8))

        self.delete_btn = ctk.CTkButton(
            btn_frame, 
            text="Sil / Delete", 
            width=85,
            fg_color=("gray75", "gray35"),
            hover_color=("gray65", "gray45"),
            command=self.delete_selected
        )
        self.delete_btn.pack(side="left", padx=(0, 8))

        self.clear_btn = ctk.CTkButton(
            btn_frame, 
            text=self.gt("hist_clear_btn"), 
            width=130,
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

        # 1. Load Settings & Configuration
        self.settings = SettingsManager()
        self.current_theme = self.settings.get("theme", "dark")
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme("blue")

        # Window settings
        self.title("LocalDictionary (TR ⇄ EN) - Portable")
        self.geometry("1060x760")
        self.minsize(860, 600)

        # 2. Initialize Database, History, and Syntax Engine
        try:
            self.db = DictionaryDB()
        except Exception as e:
            self.show_fatal_error(str(e))
            return

        self.history = HistoryManager()
        self.syntax_translator = SyntaxTranslator()
        self.history_window: Optional[HistoryWindow] = None
        self.current_popup: Optional[QuickTranslatePopup] = None

        self.debounce_timer: Optional[str] = None
        self.current_results: List[Dict[str, Any]] = []

        # 3. Setup GUI Components
        self.setup_ui()
        self.apply_treeview_theme()
        self.update_quick_history()

        # 4. Attach In-App Context Menus
        self.setup_context_menus()

        # 5. Start Global Quick Translate Service
        self.quick_service = GlobalQuickTranslateService(self, self.settings, self.db, self.syntax_translator)
        self.quick_service.start()

        # Initial search hint
        self.search_entry.focus()
        self.perform_search("welcome", save_to_history=False)

    def gt(self, key: str) -> str:
        """Localization helper."""
        return self.settings.get_text(key)

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
            text=self.gt("app_title"), 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(side="left", padx=(18, 5), pady=12)

        self.sub_label = ctk.CTkLabel(
            self.header_frame, 
            text=self.gt("app_subtitle"), 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.sub_label.pack(side="left", padx=0, pady=(15, 12))

        # Settings Button
        self.settings_btn = ctk.CTkButton(
            self.header_frame, 
            text=self.gt("settings_btn"), 
            width=90,
            height=30,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=self.open_settings_tab
        )
        self.settings_btn.pack(side="right", padx=16, pady=12)

        # History Button
        self.history_btn = ctk.CTkButton(
            self.header_frame,
            text=self.gt("history_btn"),
            width=85,
            height=30,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=self.open_history_window
        )
        self.history_btn.pack(side="right", padx=(0, 10), pady=12)

        # 2. Main Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=(4, 0))

        self.tab_dict_name = self.gt("tab_dict")
        self.tab_sentence_name = self.gt("tab_sentence")
        self.tab_settings_name = self.gt("tab_settings")

        self.tab_dict = self.tabview.add(self.tab_dict_name)
        self.tab_sentence = self.tabview.add(self.tab_sentence_name)
        self.tab_settings = self.tabview.add(self.tab_settings_name)

        self.setup_dictionary_tab()
        self.setup_sentence_tab()
        self.setup_settings_tab()

        # 3. Bottom Status Bar
        self.status_bar = ctk.CTkFrame(self, height=32, corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)

        self.status_left = ctk.CTkLabel(
            self.status_bar, 
            text=self.gt("status_ready"), 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_left.pack(side="left", padx=18)

        self.status_right = ctk.CTkLabel(
            self.status_bar, 
            text=self.gt("status_engine_badge"), 
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50"
        )
        self.status_right.pack(side="right", padx=18)

    # ---------------- TAB 1: DICTIONARY ----------------
    def setup_dictionary_tab(self):
        dir_frame = ctk.CTkFrame(self.tab_dict, fg_color="transparent")
        dir_frame.pack(fill="x", padx=4, pady=(2, 6))

        self.dict_dir_lbl = ctk.CTkLabel(dir_frame, text=self.gt("search_dir_lbl"), font=ctk.CTkFont(size=12), text_color="gray")
        self.dict_dir_lbl.pack(side="left", padx=(0, 8))

        self.dir_selector = ctk.CTkSegmentedButton(
            dir_frame,
            values=[self.gt("dir_auto"), self.gt("dir_en_tr"), self.gt("dir_tr_en")],
            command=lambda val: self.on_search_change()
        )
        self.dir_selector.set(self.gt("dir_auto"))
        self.dir_selector.pack(side="left")

        # Search box frame
        self.search_frame = ctk.CTkFrame(self.tab_dict, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=4, pady=(2, 2))

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text=self.gt("search_placeholder"),
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", self.on_key_release)
        self.search_entry.bind("<Return>", lambda e: self.perform_search(self.search_entry.get()))

        self.clear_btn = ctk.CTkButton(
            self.search_frame,
            text=self.gt("clear_btn"),
            width=38,
            height=40,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=self.clear_search
        )
        self.clear_btn.pack(side="left", padx=(0, 8))

        self.search_btn = ctk.CTkButton(
            self.search_frame,
            text=self.gt("search_btn"),
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
        
        self.tree.heading("source", text=self.gt("col_source"))
        self.tree.heading("type", text=self.gt("col_type"))
        self.tree.heading("category", text=self.gt("col_category"))
        self.tree.heading("target", text=self.gt("col_target"))

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
            text=self.gt("dict_detail_title"), 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.detail_title.pack(side="left")

        self.copy_btn = ctk.CTkButton(
            self.detail_header,
            text=self.gt("copy_translation_btn"),
            width=120,
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

        self.sent_dir_lbl = ctk.CTkLabel(opt_frame, text=self.gt("sent_dir_lbl"), font=ctk.CTkFont(size=12), text_color="gray")
        self.sent_dir_lbl.pack(side="left", padx=(0, 8))

        self.sent_dir_selector = ctk.CTkSegmentedButton(
            opt_frame,
            values=[self.gt("sent_dir_auto"), self.gt("sent_dir_en_tr"), self.gt("sent_dir_tr_en")]
        )
        self.sent_dir_selector.set(self.gt("sent_dir_auto"))
        self.sent_dir_selector.pack(side="left")

        # Source input section
        src_lbl_frame = ctk.CTkFrame(self.tab_sentence, fg_color="transparent")
        src_lbl_frame.pack(fill="x", padx=6, pady=(2, 2))

        self.sent_input_lbl = ctk.CTkLabel(src_lbl_frame, text=self.gt("sent_input_lbl"), font=ctk.CTkFont(size=13, weight="bold"))
        self.sent_input_lbl.pack(side="left")

        self.sent_input = ctk.CTkTextbox(self.tab_sentence, height=75, font=ctk.CTkFont(size=13), wrap="word")
        self.sent_input.pack(fill="x", padx=6, pady=(0, 6))

        # Action buttons
        btn_frame = ctk.CTkFrame(self.tab_sentence, fg_color="transparent")
        btn_frame.pack(fill="x", padx=6, pady=(0, 6))

        self.translate_action_btn = ctk.CTkButton(
            btn_frame,
            text=self.gt("translate_action_btn"),
            width=230,
            height=32,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.start_sentence_translation
        )
        self.translate_action_btn.pack(side="left", padx=(0, 8))

        self.sent_clear_btn = ctk.CTkButton(
            btn_frame,
            text=self.gt("sent_clear_btn"),
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

        self.sent_output_lbl = ctk.CTkLabel(tgt_lbl_frame, text=self.gt("sent_status_ready"), font=ctk.CTkFont(size=13, weight="bold"))
        self.sent_output_lbl.pack(side="left")

        self.sent_copy_btn = ctk.CTkButton(
            tgt_lbl_frame,
            text=self.gt("sent_copy_btn"),
            width=120,
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

        self.breakdown_lbl = ctk.CTkLabel(breakdown_lbl_frame, text=self.gt("breakdown_title"), font=ctk.CTkFont(size=12, weight="bold"))
        self.breakdown_lbl.pack(side="left")

        self.breakdown_frame = ctk.CTkFrame(self.tab_sentence)
        self.breakdown_frame.pack(fill="both", expand=True, padx=6, pady=(0, 4))

        b_cols = ("original", "role", "pos", "translated", "alts")
        self.breakdown_tree = ttk.Treeview(self.breakdown_frame, columns=b_cols, show="headings", selectmode="browse")
        
        self.breakdown_tree.heading("original", text=self.gt("col_orig"))
        self.breakdown_tree.heading("role", text=self.gt("col_role"))
        self.breakdown_tree.heading("pos", text=self.gt("col_pos"))
        self.breakdown_tree.heading("translated", text=self.gt("col_trans"))
        self.breakdown_tree.heading("alts", text=self.gt("col_alts"))

        self.breakdown_tree.column("original", width=160)
        self.breakdown_tree.column("role", width=110, anchor="center")
        self.breakdown_tree.column("pos", width=90, anchor="center")
        self.breakdown_tree.column("translated", width=180)
        self.breakdown_tree.column("alts", width=250)

        b_scroll = ttk.Scrollbar(self.breakdown_frame, orient="vertical", command=self.breakdown_tree.yview)
        self.breakdown_tree.configure(yscrollcommand=b_scroll.set)
        
        self.breakdown_tree.pack(side="left", fill="both", expand=True)
        b_scroll.pack(side="right", fill="y")

    # ---------------- TAB 3: SETTINGS ----------------
    def setup_settings_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_settings, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=8, pady=6)

        # Header Title
        self.lbl_settings_head = ctk.CTkLabel(
            scroll, 
            text=self.gt("settings_header"), 
            font=ctk.CTkFont(size=17, weight="bold")
        )
        self.lbl_settings_head.pack(anchor="w", padx=8, pady=(4, 2))

        self.lbl_settings_sub = ctk.CTkLabel(
            scroll, 
            text=self.gt("settings_desc"), 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.lbl_settings_sub.pack(anchor="w", padx=8, pady=(0, 12))

        # CARD 1: Appearance & Theme
        card_theme = ctk.CTkFrame(scroll)
        card_theme.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_appearance = ctk.CTkLabel(
            card_theme, 
            text=self.gt("sec_appearance"), 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_appearance.pack(anchor="w", padx=16, pady=(12, 6))

        row_theme = ctk.CTkFrame(card_theme, fg_color="transparent")
        row_theme.pack(fill="x", padx=16, pady=(0, 14))

        self.lbl_theme = ctk.CTkLabel(row_theme, text=self.gt("theme_lbl"), font=ctk.CTkFont(size=12))
        self.lbl_theme.pack(side="left", padx=(0, 12))

        cur_t = self.settings.get("theme", "dark")
        theme_map = {"dark": self.gt("theme_dark"), "light": self.gt("theme_light"), "system": self.gt("theme_system")}
        self.theme_selector = ctk.CTkSegmentedButton(
            row_theme,
            values=[self.gt("theme_dark"), self.gt("theme_light"), self.gt("theme_system")],
            command=self.on_theme_changed
        )
        self.theme_selector.set(theme_map.get(cur_t, self.gt("theme_dark")))
        self.theme_selector.pack(side="left")

        # CARD 2: Language & Interface
        card_lang = ctk.CTkFrame(scroll)
        card_lang.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_lang = ctk.CTkLabel(
            card_lang, 
            text=self.gt("sec_language"), 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_lang.pack(anchor="w", padx=16, pady=(12, 6))

        row_lang = ctk.CTkFrame(card_lang, fg_color="transparent")
        row_lang.pack(fill="x", padx=16, pady=(0, 14))

        self.lbl_lang = ctk.CTkLabel(row_lang, text=self.gt("lang_lbl"), font=ctk.CTkFont(size=12))
        self.lbl_lang.pack(side="left", padx=(0, 12))

        cur_l = self.settings.get("language", "tr")
        self.lang_selector = ctk.CTkSegmentedButton(
            row_lang,
            values=[self.gt("lang_tr"), self.gt("lang_en")],
            command=self.on_language_changed
        )
        self.lang_selector.set(self.gt("lang_tr") if cur_l == "tr" else self.gt("lang_en"))
        self.lang_selector.pack(side="left")

        # CARD 3: Right-Click & Quick Translation
        card_rc = ctk.CTkFrame(scroll)
        card_rc.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_rc = ctk.CTkLabel(
            card_rc, 
            text=self.gt("sec_right_click"), 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_rc.pack(anchor="w", padx=16, pady=(12, 4))

        # Switch 1: Enable Quick Translate Popup
        self.rc_switch = ctk.CTkSwitch(
            card_rc,
            text=self.gt("rc_enable_lbl"),
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.on_rc_switch_changed
        )
        if self.settings.get("right_click_translate", True):
            self.rc_switch.select()
        else:
            self.rc_switch.deselect()
        self.rc_switch.pack(anchor="w", padx=16, pady=(6, 2))

        self.lbl_rc_desc = ctk.CTkLabel(
            card_rc,
            text=self.gt("rc_enable_desc"),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.lbl_rc_desc.pack(anchor="w", padx=16, pady=(0, 8))

        # Trigger option
        row_trigger = ctk.CTkFrame(card_rc, fg_color="transparent")
        row_trigger.pack(fill="x", padx=16, pady=(0, 10))

        self.lbl_trigger = ctk.CTkLabel(row_trigger, text=self.gt("rc_trigger_lbl"), font=ctk.CTkFont(size=12))
        self.lbl_trigger.pack(side="left", padx=(0, 12))

        cur_trig = self.settings.get("right_click_trigger", "ctrl_right_click")
        self.trigger_selector = ctk.CTkSegmentedButton(
            row_trigger,
            values=[self.gt("trigger_ctrl_rc"), self.gt("trigger_clipboard")],
            command=self.on_trigger_changed
        )
        self.trigger_selector.set(self.gt("trigger_ctrl_rc") if cur_trig == "ctrl_right_click" else self.gt("trigger_clipboard"))
        self.trigger_selector.pack(side="left")

        # Switch 2: In-App Right Click Context Menu
        self.inapp_switch = ctk.CTkSwitch(
            card_rc,
            text=self.gt("rc_inapp_lbl"),
            font=ctk.CTkFont(size=12),
            command=self.on_inapp_switch_changed
        )
        if self.settings.get("in_app_context_menu", True):
            self.inapp_switch.select()
        else:
            self.inapp_switch.deselect()
        self.inapp_switch.pack(anchor="w", padx=16, pady=(4, 2))

        self.lbl_inapp_desc = ctk.CTkLabel(
            card_rc,
            text=self.gt("rc_inapp_desc"),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.lbl_inapp_desc.pack(anchor="w", padx=16, pady=(0, 14))

        # CARD 4: History & Storage
        card_hist = ctk.CTkFrame(scroll)
        card_hist.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_hist = ctk.CTkLabel(
            card_hist, 
            text=self.gt("sec_history"), 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_hist.pack(anchor="w", padx=16, pady=(12, 4))

        self.hist_save_switch = ctk.CTkSwitch(
            card_hist,
            text=self.gt("hist_save_lbl"),
            font=ctk.CTkFont(size=12),
            command=self.on_hist_save_changed
        )
        if self.settings.get("save_history", True):
            self.hist_save_switch.select()
        else:
            self.hist_save_switch.deselect()
        self.hist_save_switch.pack(anchor="w", padx=16, pady=(4, 2))

        self.lbl_hist_desc = ctk.CTkLabel(
            card_hist,
            text=self.gt("hist_save_desc"),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.lbl_hist_desc.pack(anchor="w", padx=16, pady=(0, 10))

        row_hist_btn = ctk.CTkFrame(card_hist, fg_color="transparent")
        row_hist_btn.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_clear_hist = ctk.CTkButton(
            row_hist_btn,
            text=self.gt("hist_clear_btn"),
            width=150,
            height=30,
            fg_color=("gray75", "gray30"),
            hover_color=("#D32F2F", "#B71C1C"),
            command=self.clear_all_history_from_settings
        )
        self.btn_clear_hist.pack(side="left")

        # CARD 5: About & System Info
        card_about = ctk.CTkFrame(scroll)
        card_about.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_about = ctk.CTkLabel(
            card_about, 
            text=self.gt("sec_about"), 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_about.pack(anchor="w", padx=16, pady=(12, 6))

        for item_key in ["about_ver", "about_db", "about_mode", "about_license"]:
            lbl = ctk.CTkLabel(card_about, text=f"• {self.gt(item_key)}", font=ctk.CTkFont(size=12))
            lbl.pack(anchor="w", padx=22, pady=2)
        
        ctk.CTkFrame(card_about, height=10, fg_color="transparent").pack()

    # ---------------- SETTINGS ACTIONS ----------------
    def on_theme_changed(self, choice):
        if "Koyu" in choice or "Dark" in choice:
            mode = "dark"
        elif "Açık" in choice or "Light" in choice:
            mode = "light"
        else:
            mode = "system"
        self.current_theme = mode
        ctk.set_appearance_mode(mode)
        self.settings.set("theme", mode)
        self.apply_treeview_theme()

    def on_language_changed(self, choice):
        lang = "tr" if "Türkçe" in choice else "en"
        self.settings.set("language", lang)
        self.apply_language()

    def on_rc_switch_changed(self):
        val = bool(self.rc_switch.get())
        self.settings.set("right_click_translate", val)

    def on_trigger_changed(self, choice):
        val = "ctrl_right_click" if "Ctrl" in choice else "clipboard"
        self.settings.set("right_click_trigger", val)

    def on_inapp_switch_changed(self):
        val = bool(self.inapp_switch.get())
        self.settings.set("in_app_context_menu", val)

    def on_hist_save_changed(self):
        val = bool(self.hist_save_switch.get())
        self.settings.set("save_history", val)

    def clear_all_history_from_settings(self):
        if messagebox.askyesno(self.gt("hist_clear_btn"), "Tüm arama geçmişiniz silinsin mi?", parent=self):
            self.history.clear_all()
            self.update_quick_history()
            self.status_left.configure(text=self.gt("hist_cleared_msg"))

    def open_settings_tab(self):
        self.tabview.set(self.tab_settings_name)

    def apply_language(self):
        """Dynamically re-labels all GUI elements to the selected language."""
        # 1. Update Tabs
        old_dict = self.tab_dict_name
        old_sent = self.tab_sentence_name
        old_sett = self.tab_settings_name

        new_dict = self.gt("tab_dict")
        new_sent = self.gt("tab_sentence")
        new_sett = self.gt("tab_settings")

        if old_dict != new_dict:
            self.tabview.rename(old_dict, new_dict)
            self.tab_dict_name = new_dict
        if old_sent != new_sent:
            self.tabview.rename(old_sent, new_sent)
            self.tab_sentence_name = new_sent
        if old_sett != new_sett:
            self.tabview.rename(old_sett, new_sett)
            self.tab_settings_name = new_sett

        # 2. Header
        self.title_label.configure(text=self.gt("app_title"))
        self.sub_label.configure(text=self.gt("app_subtitle"))
        self.settings_btn.configure(text=self.gt("settings_btn"))
        self.history_btn.configure(text=self.gt("history_btn"))

        # 3. Dictionary Tab
        self.dict_dir_lbl.configure(text=self.gt("search_dir_lbl"))
        cur_d = self.dir_selector.get()
        self.dir_selector.configure(values=[self.gt("dir_auto"), self.gt("dir_en_tr"), self.gt("dir_tr_en")])
        self.dir_selector.set(self.gt("dir_auto"))
        self.search_entry.configure(placeholder_text=self.gt("search_placeholder"))
        self.search_btn.configure(text=self.gt("search_btn"))
        self.clear_btn.configure(text=self.gt("clear_btn"))
        self.tree.heading("source", text=self.gt("col_source"))
        self.tree.heading("type", text=self.gt("col_type"))
        self.tree.heading("category", text=self.gt("col_category"))
        self.tree.heading("target", text=self.gt("col_target"))
        self.detail_title.configure(text=self.gt("dict_detail_title"))
        self.copy_btn.configure(text=self.gt("copy_translation_btn"))

        # 4. Sentence Tab
        self.sent_dir_lbl.configure(text=self.gt("sent_dir_lbl"))
        self.sent_dir_selector.configure(values=[self.gt("sent_dir_auto"), self.gt("sent_dir_en_tr"), self.gt("sent_dir_tr_en")])
        self.sent_dir_selector.set(self.gt("sent_dir_auto"))
        self.sent_input_lbl.configure(text=self.gt("sent_input_lbl"))
        self.translate_action_btn.configure(text=self.gt("translate_action_btn"))
        self.sent_clear_btn.configure(text=self.gt("sent_clear_btn"))
        self.sent_copy_btn.configure(text=self.gt("sent_copy_btn"))
        self.sent_output_lbl.configure(text=self.gt("sent_status_ready"))
        self.breakdown_lbl.configure(text=self.gt("breakdown_title"))
        self.breakdown_tree.heading("original", text=self.gt("col_orig"))
        self.breakdown_tree.heading("role", text=self.gt("col_role"))
        self.breakdown_tree.heading("pos", text=self.gt("col_pos"))
        self.breakdown_tree.heading("translated", text=self.gt("col_trans"))
        self.breakdown_tree.heading("alts", text=self.gt("col_alts"))

        # 5. Settings Tab
        self.lbl_settings_head.configure(text=self.gt("settings_header"))
        self.lbl_settings_sub.configure(text=self.gt("settings_desc"))
        self.lbl_sec_appearance.configure(text=self.gt("sec_appearance"))
        self.lbl_theme.configure(text=self.gt("theme_lbl"))
        self.theme_selector.configure(values=[self.gt("theme_dark"), self.gt("theme_light"), self.gt("theme_system")])
        cur_t = self.settings.get("theme", "dark")
        theme_map = {"dark": self.gt("theme_dark"), "light": self.gt("theme_light"), "system": self.gt("theme_system")}
        self.theme_selector.set(theme_map.get(cur_t, self.gt("theme_dark")))

        self.lbl_sec_lang.configure(text=self.gt("sec_language"))
        self.lbl_lang.configure(text=self.gt("lang_lbl"))
        self.lang_selector.configure(values=[self.gt("lang_tr"), self.gt("lang_en")])
        cur_l = self.settings.get("language", "tr")
        self.lang_selector.set(self.gt("lang_tr") if cur_l == "tr" else self.gt("lang_en"))

        self.lbl_sec_rc.configure(text=self.gt("sec_right_click"))
        self.rc_switch.configure(text=self.gt("rc_enable_lbl"))
        self.lbl_rc_desc.configure(text=self.gt("rc_enable_desc"))
        self.lbl_trigger.configure(text=self.gt("rc_trigger_lbl"))
        self.trigger_selector.configure(values=[self.gt("trigger_ctrl_rc"), self.gt("trigger_clipboard")])
        cur_trig = self.settings.get("right_click_trigger", "ctrl_right_click")
        self.trigger_selector.set(self.gt("trigger_ctrl_rc") if cur_trig == "ctrl_right_click" else self.gt("trigger_clipboard"))
        self.inapp_switch.configure(text=self.gt("rc_inapp_lbl"))
        self.lbl_inapp_desc.configure(text=self.gt("rc_inapp_desc"))

        self.lbl_sec_hist.configure(text=self.gt("sec_history"))
        self.hist_save_switch.configure(text=self.gt("hist_save_lbl"))
        self.lbl_hist_desc.configure(text=self.gt("hist_save_desc"))
        self.btn_clear_hist.configure(text=self.gt("hist_clear_btn"))
        self.lbl_sec_about.configure(text=self.gt("sec_about"))

        # 6. Status Bar
        self.status_right.configure(text=self.gt("status_engine_badge"))
        self.status_left.configure(text=self.gt("status_ready"))

    def setup_context_menus(self):
        """Attaches right click context menu to all interactive widgets."""
        attach_context_menu(self.search_entry, on_search=self.quick_search, on_sentence=self.send_to_sentence, get_text_fn=self.gt)
        attach_context_menu(self.detail_text, on_search=self.quick_search, on_sentence=self.send_to_sentence, get_text_fn=self.gt)
        attach_context_menu(self.sent_input, on_search=self.quick_search, on_sentence=self.send_to_sentence, get_text_fn=self.gt)
        attach_context_menu(self.sent_output, on_search=self.quick_search, on_sentence=self.send_to_sentence, get_text_fn=self.gt)

    def show_quick_popup(self, text: str, trans: str, x: int, y: int):
        try:
            if hasattr(self, "current_popup") and self.current_popup and self.current_popup.winfo_exists():
                self.current_popup.destroy()
            self.current_popup = QuickTranslatePopup(
                self, text, trans, x, y,
                on_open_in_dict=lambda q: (self.deiconify(), self.lift(), self.focus_force(), self.quick_search(q))
            )
        except Exception as e:
            print(f"Hızlı çeviri balonu hatası: {e}")

    def send_to_sentence(self, text: str):
        self.tabview.set(self.tab_sentence_name)
        self.sent_input.delete("0.0", "end")
        self.sent_input.delete("1.0", "end")
        self.sent_input.insert("0.0", text)
        self.start_sentence_translation()

    # ---------------- SENTENCE TRANSLATION ACTIONS ----------------
    def clear_sentence_inputs(self):
        self.sent_input.delete("0.0", "end")
        self.sent_input.delete("1.0", "end")
        
        self.sent_output.configure(state="normal")
        self.sent_output.delete("0.0", "end")
        self.sent_output.delete("1.0", "end")
        self.sent_output.configure(state="disabled")

        for item in self.breakdown_tree.get_children():
            self.breakdown_tree.delete(item)

        self.sent_loading_lbl.configure(text="")
        self.status_left.configure(text=self.gt("sent_clear_btn"))
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
        if choice in ("İngilizce ➔ Türkçe", "English ➔ Turkish"):
            dir_code = "en_tr"
        elif choice in ("Türkçe ➔ İngilizce", "Turkish ➔ English"):
            dir_code = "tr_en"
        else:
            dir_code = "auto"

        res = self.syntax_translator.translate(text, direction=dir_code)
        
        self.sent_output.configure(state="normal")
        self.sent_output.delete("0.0", "end")
        self.sent_output.delete("1.0", "end")
        self.sent_output.insert("0.0", res["translated_text"])
        self.sent_output.configure(state="disabled")

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

        self.sent_loading_lbl.configure(text=self.gt("sent_loading_done"))
        self.status_left.configure(text=self.gt("sent_status_ready"))

    # ---------------- UTILITY / THEME / COMMON ----------------
    def update_quick_history(self):
        for child in self.quick_history_frame.winfo_children():
            child.destroy()

        recent = self.history.get_recent(limit=6)
        if not recent:
            return

        lbl = ctk.CTkLabel(
            self.quick_history_frame, 
            text=self.gt("recent_searches"), 
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
        self.tabview.set(self.tab_dict_name)
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, word)
        self.perform_search(word)

    def open_history_window(self):
        if self.history_window is None or not self.history_window.winfo_exists():
            self.history_window = HistoryWindow(self, self.history, self.quick_search, self.settings)
        else:
            self.history_window.focus()

    def apply_treeview_theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        mode = self.current_theme
        if mode == "system":
            import darkdetect
            mode = "dark" if darkdetect.isDark() else "light"

        if mode == "dark":
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
        self.status_left.configure(text=self.gt("status_ready"))

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
        if sel_mode in ("EN ➔ TR", "İngilizce ➔ Türkçe"):
            mode = "en_tr"
        elif sel_mode in ("TR ➔ EN", "Türkçe ➔ İngilizce"):
            mode = "tr_en"
        else:
            mode = "auto"

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
            
            if save_to_history and len(query) >= 2 and self.settings.get("save_history", True):
                self.history.add_search(query, detected_dir, len(results))
                self.update_quick_history()
        else:
            self.show_no_results(query)

        res_msg = self.gt("results_found").format(count=len(results), ms=elapsed_ms, direction=detected_dir)
        self.status_left.configure(text=res_msg)

    def show_no_results(self, query: str):
        msg = self.gt("no_results").format(query=query)
        self.set_detail_text(msg)

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
            self.status_left.configure(text=self.gt("copied_status").format(word=target))
            self.after(1500, lambda: self.status_left.configure(text=old_status))

    def destroy(self):
        if hasattr(self, "debounce_timer") and self.debounce_timer:
            try:
                self.after_cancel(self.debounce_timer)
            except Exception:
                pass
        if hasattr(self, "quick_service") and self.quick_service:
            self.quick_service.stop()
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

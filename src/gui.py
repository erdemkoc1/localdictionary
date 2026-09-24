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
from src.translator import SentenceTranslator
from src.spell_checker import SpellChecker
from src.settings import SettingsManager
from src.quick_translate import QuickTranslatePopup, QuickTranslateButton, GlobalQuickTranslateService, attach_context_menu
from src.platform_win import (
    set_app_user_model_id, 
    set_windows_startup, 
    get_windows_startup, 
    set_windows_context_menu, 
    get_windows_context_menu
)
from src.tray import AppTrayIcon
from src.grammar_normalizer import normalize_pos, normalize_role


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
        self.tree.heading("time", text=self.gt("col_time"))

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
            text=self.gt("btn_delete"), 
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
        if messagebox.askyesno(self.gt("hist_clear_confirm_title"), self.gt("hist_clear_confirm_msg"), parent=self):
            self.history_manager.clear_all()
            self.load_history()
            self.parent.update_quick_history()


class SettingsWindow(ctk.CTkToplevel):
    """
    Dedicated Modern Modal Settings Window.
    Separates Dual Right-Click Translation options and Windows Startup options clearly.
    """
    def __init__(self, parent, settings_mgr: SettingsManager):
        super().__init__(parent)
        self.parent = parent
        self.settings = settings_mgr

        self.title(self.gt("settings_window_title"))
        self.geometry("660x680")
        self.minsize(540, 500)
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

    def gt(self, key: str) -> str:
        return self.settings.get_text(key)

    def setup_ui(self):
        # Header
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(16, 6))

        self.lbl_head = ctk.CTkLabel(
            top_frame,
            text=self.gt("settings_window_title"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_head.pack(anchor="w")

        self.lbl_sub = ctk.CTkLabel(
            top_frame,
            text=self.gt("settings_window_sub"),
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.lbl_sub.pack(anchor="w", pady=(2, 0))

        # Scrollable container for cards
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=14, pady=6)

        # ---------------- CARD 1: Appearance & Window ----------------
        card_theme = ctk.CTkFrame(self.scroll)
        card_theme.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_appearance = ctk.CTkLabel(
            card_theme,
            text=self.gt("sec_appearance"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_appearance.pack(anchor="w", padx=16, pady=(12, 6))

        row_theme = ctk.CTkFrame(card_theme, fg_color="transparent")
        row_theme.pack(fill="x", padx=16, pady=(0, 10))

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

        # Always on top switch
        self.always_on_top_switch = ctk.CTkSwitch(
            card_theme,
            text=self.gt("always_on_top_lbl"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_always_on_top_changed
        )
        if self.settings.get("always_on_top", False):
            self.always_on_top_switch.select()
        else:
            self.always_on_top_switch.deselect()
        self.always_on_top_switch.pack(anchor="w", padx=16, pady=(4, 2))

        self.lbl_always_on_top_desc = ctk.CTkLabel(
            card_theme,
            text=self.gt("always_on_top_desc"),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.lbl_always_on_top_desc.pack(anchor="w", padx=16, pady=(0, 12))

        # ---------------- CARD 2: Language & Interface ----------------
        card_lang = ctk.CTkFrame(self.scroll)
        card_lang.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_lang = ctk.CTkLabel(
            card_lang,
            text=self.gt("sec_language"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_lang.pack(anchor="w", padx=16, pady=(12, 6))

        row_lang = ctk.CTkFrame(card_lang, fg_color="transparent")
        row_lang.pack(fill="x", padx=16, pady=(0, 12))

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

        # ---------------- CARD 3: Dual Right-Click Options ----------------
        card_rc = ctk.CTkFrame(self.scroll)
        card_rc.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_rc = ctk.CTkLabel(
            card_rc,
            text=self.gt("sec_right_click_options"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_rc.pack(anchor="w", padx=16, pady=(12, 6))

        # Feature 1: Selection Translate (Floating Button on Text Drag-Selection in Brave, Chrome, etc.)
        self.selection_switch = ctk.CTkSwitch(
            card_rc,
            text=self.gt("selection_translate_lbl"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_selection_changed
        )
        if self.settings.get("selection_translate", True):
            self.selection_switch.select()
        else:
            self.selection_switch.deselect()
        self.selection_switch.pack(anchor="w", padx=16, pady=(4, 2))

        self.lbl_selection_desc = ctk.CTkLabel(
            card_rc,
            text=self.gt("selection_translate_desc"),
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=540,
            justify="left"
        )
        self.lbl_selection_desc.pack(anchor="w", padx=16, pady=(0, 8))

        # Feature 1b: Double-Click Translate (Floating Button on Word Double-Click)
        self.double_click_switch = ctk.CTkSwitch(
            card_rc,
            text=self.gt("double_click_translate_lbl"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_double_click_changed
        )
        if self.settings.get("double_click_translate", False):
            self.double_click_switch.select()
        else:
            self.double_click_switch.deselect()
        self.double_click_switch.pack(anchor="w", padx=16, pady=(4, 2))

        self.lbl_double_click_desc = ctk.CTkLabel(
            card_rc,
            text=self.gt("double_click_translate_desc"),
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=540,
            justify="left"
        )
        self.lbl_double_click_desc.pack(anchor="w", padx=16, pady=(0, 10))

        # Feature 2: Ctrl + Right Click Quick Translate Popup
        self.ctrl_rc_switch = ctk.CTkSwitch(
            card_rc,
            text=self.gt("ctrl_rc_lbl"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_ctrl_rc_changed
        )
        if self.settings.get("ctrl_right_click_translate", True):
            self.ctrl_rc_switch.select()
        else:
            self.ctrl_rc_switch.deselect()
        self.ctrl_rc_switch.pack(anchor="w", padx=16, pady=(4, 2))

        self.lbl_ctrl_rc_desc = ctk.CTkLabel(
            card_rc,
            text=self.gt("ctrl_rc_desc"),
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=540,
            justify="left"
        )
        self.lbl_ctrl_rc_desc.pack(anchor="w", padx=16, pady=(0, 10))

        # Feature 3: Windows Shell Context Menu ("LocalDictionary ile Çevir") & Right-Click Button
        self.win_ctx_switch = ctk.CTkSwitch(
            card_rc,
            text=self.gt("win_ctx_lbl"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_win_ctx_changed
        )
        reg_ctx = get_windows_context_menu()
        desc_text = self.gt("win_ctx_desc")
        desc_color = "gray"
        if reg_ctx or self.settings.get("windows_context_menu", False):
            self.win_ctx_switch.select()
            desc_text += "\n" + self.gt("win_ctx_active_notice")
            desc_color = "#4CAF50"
        else:
            self.win_ctx_switch.deselect()
        self.win_ctx_switch.pack(anchor="w", padx=16, pady=(4, 2))

        self.lbl_win_ctx_desc = ctk.CTkLabel(
            card_rc,
            text=desc_text,
            font=ctk.CTkFont(size=11),
            text_color=desc_color,
            wraplength=540,
            justify="left"
        )
        self.lbl_win_ctx_desc.pack(anchor="w", padx=16, pady=(0, 10))

        # In-App Context Menu
        self.inapp_switch = ctk.CTkSwitch(
            card_rc,
            text=self.gt("rc_inapp_lbl"),
            font=ctk.CTkFont(size=12),
            command=self.on_inapp_changed
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
        self.lbl_inapp_desc.pack(anchor="w", padx=16, pady=(0, 12))

        # ---------------- CARD 4: Windows Startup Preferences ----------------
        card_start = ctk.CTkFrame(self.scroll)
        card_start.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_startup = ctk.CTkLabel(
            card_start,
            text=self.gt("sec_startup"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_startup.pack(anchor="w", padx=16, pady=(12, 6))

        reg_start, reg_mode = get_windows_startup()
        cur_start = reg_start or self.settings.get("run_on_startup", False)

        self.startup_switch = ctk.CTkSwitch(
            card_start,
            text=self.gt("startup_enable_lbl"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_startup_changed
        )
        if cur_start:
            self.startup_switch.select()
        else:
            self.startup_switch.deselect()
        self.startup_switch.pack(anchor="w", padx=16, pady=(4, 2))

        self.lbl_startup_desc = ctk.CTkLabel(
            card_start,
            text=self.gt("startup_enable_desc"),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.lbl_startup_desc.pack(anchor="w", padx=16, pady=(0, 10))

        # Startup launch state row
        row_mode = ctk.CTkFrame(card_start, fg_color="transparent")
        row_mode.pack(fill="x", padx=16, pady=(0, 6))

        self.lbl_startup_mode = ctk.CTkLabel(row_mode, text=self.gt("startup_mode_lbl"), font=ctk.CTkFont(size=12))
        self.lbl_startup_mode.pack(anchor="w", pady=(0, 4))

        cur_mode = reg_mode if reg_start else self.settings.get("startup_mode", "normal")
        self.mode_selector = ctk.CTkSegmentedButton(
            row_mode,
            values=[self.gt("startup_mode_normal"), self.gt("startup_mode_minimized")],
            command=self.on_startup_mode_changed
        )
        self.mode_selector.set(self.gt("startup_mode_normal") if cur_mode == "normal" else self.gt("startup_mode_minimized"))
        self.mode_selector.pack(fill="x", pady=(2, 4))

        self.lbl_mode_desc = ctk.CTkLabel(
            card_start,
            text=self.gt("startup_mode_desc"),
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=540,
            justify="left"
        )
        self.lbl_mode_desc.pack(anchor="w", padx=16, pady=(0, 12))

        # ---------------- CARD 5: Taskbar & System Tray ----------------
        card_tray = ctk.CTkFrame(self.scroll)
        card_tray.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_tray = ctk.CTkLabel(
            card_tray,
            text=self.gt("sec_tray"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_tray.pack(anchor="w", padx=16, pady=(12, 6))

        self.lbl_tray_status = ctk.CTkLabel(
            card_tray,
            text=self.gt("tray_desc"),
            font=ctk.CTkFont(size=11),
            text_color="#4CAF50",
            wraplength=540,
            justify="left"
        )
        self.lbl_tray_status.pack(anchor="w", padx=16, pady=(0, 8))

        self.tray_min_switch = ctk.CTkSwitch(
            card_tray,
            text=self.gt("tray_minimize_lbl"),
            font=ctk.CTkFont(size=12),
            command=self.on_tray_min_changed
        )
        if self.settings.get("minimize_to_tray", True):
            self.tray_min_switch.select()
        else:
            self.tray_min_switch.deselect()
        self.tray_min_switch.pack(anchor="w", padx=16, pady=(4, 2))

        self.lbl_tray_min_desc = ctk.CTkLabel(
            card_tray,
            text=self.gt("tray_minimize_desc"),
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=540,
            justify="left"
        )
        self.lbl_tray_min_desc.pack(anchor="w", padx=16, pady=(0, 12))

        # ---------------- CARD 6: Content Preferences ----------------
        card_content = ctk.CTkFrame(self.scroll)
        card_content.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_content = ctk.CTkLabel(
            card_content,
            text=self.gt("sec_content"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_content.pack(anchor="w", padx=16, pady=(12, 6))

        self.slang_switch = ctk.CTkSwitch(
            card_content,
            text=self.gt("slang_profanity_lbl"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_slang_changed
        )
        if self.settings.get("show_slang_profanity", True):
            self.slang_switch.select()
        else:
            self.slang_switch.deselect()
        self.slang_switch.pack(anchor="w", padx=16, pady=(4, 2))

        self.lbl_slang_desc = ctk.CTkLabel(
            card_content,
            text=self.gt("slang_profanity_desc"),
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=540,
            justify="left"
        )
        self.lbl_slang_desc.pack(anchor="w", padx=16, pady=(0, 12))

        # ---------------- CARD 7: History & Storage ----------------
        card_hist = ctk.CTkFrame(self.scroll)
        card_hist.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_hist = ctk.CTkLabel(
            card_hist,
            text=self.gt("sec_history"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_hist.pack(anchor="w", padx=16, pady=(12, 6))

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
        row_hist_btn.pack(fill="x", padx=16, pady=(0, 12))

        self.btn_clear_hist = ctk.CTkButton(
            row_hist_btn,
            text=self.gt("hist_clear_btn"),
            width=150,
            height=30,
            fg_color=("gray75", "gray30"),
            hover_color=("#D32F2F", "#B71C1C"),
            command=self.clear_all_history
        )
        self.btn_clear_hist.pack(side="left")

        # ---------------- CARD 7: System & About ----------------
        card_about = ctk.CTkFrame(self.scroll)
        card_about.pack(fill="x", padx=6, pady=6)

        self.lbl_sec_about = ctk.CTkLabel(
            card_about,
            text=self.gt("sec_about"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_sec_about.pack(anchor="w", padx=16, pady=(12, 6))

        for item_key in ["about_ver", "about_db", "about_mode", "about_license", "about_status_active"]:
            lbl = ctk.CTkLabel(card_about, text=f"• {self.gt(item_key)}", font=ctk.CTkFont(size=12))
            lbl.pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkFrame(card_about, height=10, fg_color="transparent").pack()

        # Bottom Bar
        bottom_bar = ctk.CTkFrame(self, fg_color="transparent", height=45)
        bottom_bar.pack(fill="x", padx=20, pady=(6, 12))

        self.btn_close = ctk.CTkButton(
            bottom_bar,
            text=self.gt("btn_close"),
            width=120,
            height=32,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.destroy
        )
        self.btn_close.pack(side="right")

    def on_theme_changed(self, choice):
        if "Koyu" in choice or "Dark" in choice:
            mode = "dark"
        elif "Açık" in choice or "Light" in choice:
            mode = "light"
        else:
            mode = "system"
        ctk.set_appearance_mode(mode)
        self.settings.set("theme", mode)
        self.parent.current_theme = mode
        self.parent.apply_treeview_theme()

    def on_always_on_top_changed(self):
        val = bool(self.always_on_top_switch.get())
        self.settings.set("always_on_top", val)
        self.parent.attributes("-topmost", val)

    def on_language_changed(self, choice):
        lang = "tr" if "Türkçe" in choice else "en"
        self.settings.set("language", lang)
        self.parent.apply_language()
        self.refresh_ui()

    def on_selection_changed(self):
        val = bool(self.selection_switch.get())
        self.settings.set("selection_translate", val)

    def on_double_click_changed(self):
        val = bool(self.double_click_switch.get())
        self.settings.set("double_click_translate", val)

    def on_ctrl_rc_changed(self):
        val = bool(self.ctrl_rc_switch.get())
        self.settings.set("ctrl_right_click_translate", val)

    def on_win_ctx_changed(self):
        val = bool(self.win_ctx_switch.get())
        self.settings.set("windows_context_menu", val)
        menu_title = "LocalDictionary ile Çevir" if self.settings.get("language", "tr") == "tr" else "Translate with LocalDictionary"
        set_windows_context_menu(val, menu_title)

        if val:
            # 1. Keep running in system tray when closed
            self.settings.set("minimize_to_tray", True)
            if hasattr(self, "tray_min_switch"):
                self.tray_min_switch.select()

            # 2. Enable startup in background so it starts in system tray on boot
            self.settings.set("run_on_startup", True)
            self.settings.set("startup_mode", "minimized")
            if hasattr(self, "startup_switch"):
                self.startup_switch.select()
            if hasattr(self, "mode_selector"):
                self.mode_selector.set(self.gt("startup_mode_minimized"))
            set_windows_startup(True, "minimized")

            # 3. Ensure tray icon is actively running
            if hasattr(self.parent, "tray") and self.parent.tray:
                self.parent.tray.start()

            # 4. Show success status label in green
            self.lbl_win_ctx_desc.configure(
                text=self.gt("win_ctx_desc") + "\n" + self.gt("win_ctx_active_notice"),
                text_color="#4CAF50"
            )
        else:
            self.lbl_win_ctx_desc.configure(
                text=self.gt("win_ctx_desc"),
                text_color="gray"
            )

    def on_inapp_changed(self):
        val = bool(self.inapp_switch.get())
        self.settings.set("in_app_context_menu", val)

    def on_startup_changed(self):
        val = bool(self.startup_switch.get())
        self.settings.set("run_on_startup", val)
        mode = self.settings.get("startup_mode", "normal")
        set_windows_startup(val, mode)

    def on_startup_mode_changed(self, choice):
        mode = "normal" if "Normal" in choice or "Open" in choice else "minimized"
        self.settings.set("startup_mode", mode)
        if self.settings.get("run_on_startup", False):
            set_windows_startup(True, mode)

    def on_tray_min_changed(self):
        val = bool(self.tray_min_switch.get())
        self.settings.set("minimize_to_tray", val)

    def on_slang_changed(self):
        val = bool(self.slang_switch.get())
        self.settings.set("show_slang_profanity", val)

    def on_hist_save_changed(self):
        val = bool(self.hist_save_switch.get())
        self.settings.set("save_history", val)

    def clear_all_history(self):
        if messagebox.askyesno(self.gt("hist_clear_confirm_title"), self.gt("hist_clear_confirm_msg"), parent=self):
            self.parent.history.clear_all()
            self.parent.update_quick_history()
            messagebox.showinfo(self.gt("history_btn"), self.gt("hist_cleared_msg"), parent=self)

    def refresh_ui(self):
        for child in self.winfo_children():
            child.destroy()
        self.title(self.gt("settings_window_title"))
        self.setup_ui()


class GlossaryWindow(ctk.CTkToplevel):
    """
    Dedicated Window for Managing User Custom Glossary Terms (Özel Terim Sözlüğü).
    Allows defining domain-specific term pairs (source -> target) enforced during translation.
    """
    def __init__(self, parent, user_data_mgr, settings_mgr: SettingsManager):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data_mgr
        self.settings = settings_mgr

        self.title(self.gt("glossary_title"))
        self.geometry("680x520")
        self.minsize(540, 420)
        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.load_terms()

    def gt(self, key: str) -> str:
        return self.settings.get_text(key)

    def setup_ui(self):
        # Header
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(16, 6))

        lbl_head = ctk.CTkLabel(
            top_frame,
            text=self.gt("glossary_title"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        lbl_head.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            top_frame,
            text=self.gt("glossary_sub"),
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Add Term Card
        input_card = ctk.CTkFrame(self)
        input_card.pack(fill="x", padx=16, pady=8)

        row_inputs = ctk.CTkFrame(input_card, fg_color="transparent")
        row_inputs.pack(fill="x", padx=12, pady=12)

        lbl_s = ctk.CTkLabel(row_inputs, text=self.gt("glossary_src"), font=ctk.CTkFont(size=12, weight="bold"))
        lbl_s.pack(side="left", padx=(0, 6))

        self.src_entry = ctk.CTkEntry(row_inputs, placeholder_text="e.g. prompt engineering", width=150)
        self.src_entry.pack(side="left", padx=(0, 10))

        lbl_t = ctk.CTkLabel(row_inputs, text=self.gt("glossary_tgt"), font=ctk.CTkFont(size=12, weight="bold"))
        lbl_t.pack(side="left", padx=(0, 6))

        self.tgt_entry = ctk.CTkEntry(row_inputs, placeholder_text="e.g. istem mühendisliği", width=150)
        self.tgt_entry.pack(side="left", padx=(0, 12))

        self.add_btn = ctk.CTkButton(
            row_inputs,
            text=self.gt("glossary_add"),
            width=110,
            command=self.add_term
        )
        self.add_btn.pack(side="right")

        # Treeview list
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(fill="both", expand=True, padx=16, pady=4)

        cols = ("id", "source", "target", "lang_pair", "time")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("id", text="#")
        self.tree.heading("source", text=self.gt("glossary_src").rstrip(":"))
        self.tree.heading("target", text=self.gt("glossary_tgt").rstrip(":"))
        self.tree.heading("lang_pair", text=self.gt("sent_dir_lbl").rstrip(":"))
        self.tree.heading("time", text=self.gt("col_time"))

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("source", width=170)
        self.tree.column("target", width=170)
        self.tree.column("lang_pair", width=90, anchor="center")
        self.tree.column("time", width=130, anchor="center")

        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Bottom actions
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=12)

        self.del_btn = ctk.CTkButton(
            btn_frame,
            text=self.gt("glossary_del"),
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            width=130,
            command=self.delete_selected
        )
        self.del_btn.pack(side="left")

        self.close_btn = ctk.CTkButton(
            btn_frame,
            text=self.gt("btn_close"),
            width=100,
            command=self.destroy
        )
        self.close_btn.pack(side="right")

    def load_terms(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        terms = self.user_data.get_glossary_terms()
        for t in terms:
            self.tree.insert("", "end", values=(
                t["id"],
                t["source_term"],
                t["target_term"],
                t.get("lang_pair", "all"),
                t.get("created_at", "-")
            ))

    def add_term(self):
        src = self.src_entry.get().strip()
        tgt = self.tgt_entry.get().strip()
        if not src or not tgt:
            messagebox.showwarning(self.gt("glossary_title"), "Lütfen kaynak ve hedef terimi girin.", parent=self)
            return
        self.user_data.add_glossary_term(src, tgt)
        self.src_entry.delete(0, "end")
        self.tgt_entry.delete(0, "end")
        self.load_terms()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        if vals:
            term_id = int(vals[0])
            self.user_data.delete_glossary_term(term_id)
            self.load_terms()


class CorrectionDialog(ctk.CTkToplevel):
    """
    Modal dialog allowing the user to teach and correct a translation.
    Learned corrections are stored persistently in user_data.db and prioritized
    with 100% confidence.
    """
    def __init__(self, parent, source_text: str, current_translation: str, from_lang: str, to_lang: str, on_save_callback, settings_mgr: SettingsManager):
        super().__init__(parent)
        self.parent = parent
        self.source_text = source_text
        self.current_translation = current_translation
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.on_save_callback = on_save_callback
        self.settings = settings_mgr

        self.title(self.gt("correction_title"))
        self.geometry("580x420")
        self.minsize(480, 360)
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

    def gt(self, key: str) -> str:
        return self.settings.get_text(key)

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(16, 6))

        lbl_head = ctk.CTkLabel(
            top_frame,
            text=self.gt("correction_title"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        lbl_head.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            top_frame,
            text=self.gt("correction_desc"),
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=520,
            justify="left"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Source Text Preview
        lbl_s = ctk.CTkLabel(self, text=self.gt("sent_input_lbl"), font=ctk.CTkFont(size=12, weight="bold"))
        lbl_s.pack(anchor="w", padx=20, pady=(10, 2))

        self.src_preview = ctk.CTkTextbox(self, height=65, font=ctk.CTkFont(size=12), wrap="word")
        self.src_preview.pack(fill="x", padx=20, pady=(0, 8))
        self.src_preview.insert("0.0", self.source_text)
        self.src_preview.configure(state="disabled")

        # Corrected Target Input
        lbl_t = ctk.CTkLabel(self, text=self.gt("col_trans") + ":", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_t.pack(anchor="w", padx=20, pady=(4, 2))

        self.tgt_entry = ctk.CTkTextbox(self, height=75, font=ctk.CTkFont(size=13, weight="bold"), wrap="word")
        self.tgt_entry.pack(fill="x", padx=20, pady=(0, 14))
        self.tgt_entry.insert("0.0", self.current_translation)
        self.tgt_entry.focus()

        # Action Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 16))

        self.save_btn = ctk.CTkButton(
            btn_frame,
            text=self.gt("btn_save"),
            font=ctk.CTkFont(size=13, weight="bold"),
            height=32,
            command=self.save_correction
        )
        self.save_btn.pack(side="left", padx=(0, 10))

        self.cancel_btn = ctk.CTkButton(
            btn_frame,
            text=self.gt("sent_clear_btn"),
            fg_color=("gray75", "gray35"),
            hover_color=("gray65", "gray45"),
            height=32,
            command=self.destroy
        )
        self.cancel_btn.pack(side="left")

    def save_correction(self):
        new_text = self.tgt_entry.get("1.0", "end").strip()
        if not new_text:
            messagebox.showwarning(self.gt("correction_title"), "Lütfen düzeltilmiş çeviriyi girin.", parent=self)
            return

        user_data = self.parent.sentence_translator.user_data
        user_data.save_correction(self.source_text, new_text, self.from_lang, self.to_lang)
        user_data.set_cached_translation(self.source_text, self.from_lang, self.to_lang, new_text, "user_correction", 100)

        if self.on_save_callback:
            self.on_save_callback(new_text)

        messagebox.showinfo(self.gt("correction_title"), self.gt("correction_saved"), parent=self)
        self.destroy()


class TranslatorApp(ctk.CTk):
    def __init__(self, start_minimized: bool = False):
        super().__init__()

        # Explicit Taskbar AppUserModelID
        set_app_user_model_id("LocalDictionary.App.1.41")

        # 1. Load Settings & Configuration
        self.settings = SettingsManager()
        self.current_theme = self.settings.get("theme", "dark")
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme("blue")

        # Window settings
        is_tr = self.settings.get("language", "tr") == "tr"
        badge_txt = "Açık Kaynak (BETA)" if is_tr else "Open Source (BETA)"
        self.title(f"LocalDictionary v1.41 - {badge_txt}")
        self.geometry("1060x760")
        self.minsize(860, 600)

        if self.settings.get("always_on_top", False):
            self.attributes("-topmost", True)

        # 2. Initialize Database, History, and Syntax Engine
        try:
            self.db = DictionaryDB()
        except Exception as e:
            self.show_fatal_error(str(e))
            return

        self.history = HistoryManager()
        self.spell_checker = SpellChecker(db_conn=self.db.conn)
        self.syntax_translator = SyntaxTranslator()
        self.sentence_translator = SentenceTranslator(syntax_engine=self.syntax_translator)
        self.sentence_translator.warm_up()
        self.history_window: Optional[HistoryWindow] = None
        self.settings_window: Optional[SettingsWindow] = None
        self.glossary_window: Optional[GlossaryWindow] = None
        self.correction_dialog: Optional[CorrectionDialog] = None
        self._last_translation_source: str = ""
        self._last_translation_from: str = "auto"
        self._last_translation_to: str = "auto"
        self.current_popup: Optional[QuickTranslatePopup] = None
        self.current_quick_btn: Optional[QuickTranslateButton] = None

        self.debounce_timer: Optional[str] = None
        self.current_results: List[Dict[str, Any]] = []

        # 3. Setup GUI Components (Only 2 tabs!)
        self.setup_ui()
        self.apply_treeview_theme()
        self.update_quick_history()

        # 4. Attach In-App Context Menus
        self.setup_context_menus()

        # 5. Start Global Quick Translate Service (using hybrid NMT sentence translator)
        self.quick_service = GlobalQuickTranslateService(self, self.settings, self.db, self.sentence_translator)

        self.quick_service.start()

        # 6. Start Windows System Tray Icon
        self.tray = AppTrayIcon(self, self.show_window, self.open_settings_window, self.quit_app)
        self.tray.start()

        # 7. Window Close Protocol (Minimize to tray or exit)
        self.protocol("WM_DELETE_WINDOW", self.on_close_requested)

        # 8. Start Minimized or Foreground
        is_min = start_minimized or ("--minimized" in sys.argv)
        if is_min:
            self.withdraw()
        else:
            self.search_entry.focus()
            args = [a for a in sys.argv[1:] if a != "--minimized"]
            if args:
                query = " ".join(args).strip()
                if os.path.exists(query) and os.path.isfile(query):
                    query = os.path.basename(query)
                self.perform_search(query, save_to_history=False)
            else:
                self.perform_search("welcome", save_to_history=False)

    def gt(self, key: str) -> str:
        """Localization helper."""
        return self.settings.get_text(key)

    def show_fatal_error(self, msg: str):
        card = ctk.CTkFrame(self, corner_radius=12, fg_color=("#F5F5F5", "#242424"))
        card.pack(expand=True, fill="both", padx=40, pady=40)
        
        lbl_icon = ctk.CTkLabel(card, text="⚠️", font=("Segoe UI", 48))
        lbl_icon.pack(pady=(40, 10))
        
        lbl_title = ctk.CTkLabel(card, text="Veritabanı Dosyası Bulunamadı (dictionary.db)", font=("Segoe UI", 20, "bold"))
        lbl_title.pack(pady=(0, 15))
        
        help_text = (
            f"Eksik dosya: {msg}\n\n"
            "GitHub'ın 100MB tekil dosya boyutu sınırı nedeniyle 370MB+ sözlük veritabanı\n"
            "doğrudan git reposunda tutulmamaktadır.\n\n"
            "Nasıl Çözülür?\n"
            "1. GitHub Releases sayfasından 'dictionary.db' dosyasını indirip 'data/' içine koyun, VEYA\n"
            "2. Terminalde 'python scripts/expand_dictionary_radically.py' çalıştırarak yerel oluşturun."
        )
        lbl_desc = ctk.CTkLabel(card, text=help_text, font=("Segoe UI", 13), justify="left")
        lbl_desc.pack(padx=30, pady=10)

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

        # Settings Button (Header Right)
        self.settings_btn = ctk.CTkButton(
            self.header_frame, 
            text=self.gt("settings_btn"), 
            width=90,
            height=30,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=self.open_settings_window
        )
        self.settings_btn.pack(side="right", padx=16, pady=12)

        # History Button (Header Right)
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

        # 2. Main Tabview (Only 2 tabs as requested!)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=(4, 0))

        self.tab_dict_name = self.gt("tab_dict")
        self.tab_sentence_name = self.gt("tab_sentence")

        self.tab_dict = self.tabview.add(self.tab_dict_name)
        self.tab_sentence = self.tabview.add(self.tab_sentence_name)

        self.setup_dictionary_tab()
        self.setup_sentence_tab()

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

        # "Bunu mu demek istediniz?" Suggestion Banner
        self.dict_suggestion_frame = ctk.CTkFrame(self.tab_dict, fg_color=("gray90", "gray22"), corner_radius=6, height=32)
        self.dict_suggestion_frame.pack_propagate(False)

        self.dict_suggestion_lbl = ctk.CTkLabel(
            self.dict_suggestion_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.dict_suggestion_lbl.pack(side="left", padx=(10, 4), pady=2)

        self.dict_suggestion_btn = ctk.CTkButton(
            self.dict_suggestion_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold", underline=True),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            text_color=("#1f538d", "#3B8ED0"),
            height=24,
            command=self.apply_dict_suggestion
        )
        self.dict_suggestion_btn.pack(side="left", padx=(0, 10), pady=2)

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

        self.sent_glossary_btn = ctk.CTkButton(
            opt_frame,
            text=self.gt("btn_glossary"),
            width=130,
            height=28,
            font=ctk.CTkFont(size=12),
            command=self.open_glossary_window
        )
        self.sent_glossary_btn.pack(side="right")

        # Source input section
        src_lbl_frame = ctk.CTkFrame(self.tab_sentence, fg_color="transparent")
        src_lbl_frame.pack(fill="x", padx=6, pady=(2, 2))

        self.sent_input_lbl = ctk.CTkLabel(src_lbl_frame, text=self.gt("sent_input_lbl"), font=ctk.CTkFont(size=13, weight="bold"))
        self.sent_input_lbl.pack(side="left")

        self.sent_input = ctk.CTkTextbox(self.tab_sentence, height=75, font=ctk.CTkFont(size=13), wrap="word")
        self.sent_input.pack(fill="x", padx=6, pady=(0, 6))

        # "Bunu mu demek istediniz?" Suggestion Banner
        self.sent_suggestion_frame = ctk.CTkFrame(self.tab_sentence, fg_color=("gray90", "gray22"), corner_radius=6, height=32)
        self.sent_suggestion_frame.pack_propagate(False)

        self.sent_suggestion_lbl = ctk.CTkLabel(
            self.sent_suggestion_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.sent_suggestion_lbl.pack(side="left", padx=(10, 4), pady=2)

        self.sent_suggestion_btn = ctk.CTkButton(
            self.sent_suggestion_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold", underline=True),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            text_color=("#1f538d", "#3B8ED0"),
            height=24,
            command=self.apply_sent_suggestion
        )
        self.sent_suggestion_btn.pack(side="left", padx=(0, 10), pady=2)

        # Action buttons
        self.sent_btn_frame = ctk.CTkFrame(self.tab_sentence, fg_color="transparent")
        self.sent_btn_frame.pack(fill="x", padx=6, pady=(0, 6))

        self.translate_action_btn = ctk.CTkButton(
            self.sent_btn_frame,
            text=self.gt("translate_action_btn"),
            width=230,
            height=32,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.start_sentence_translation
        )
        self.translate_action_btn.pack(side="left", padx=(0, 8))

        self.sent_clear_btn = ctk.CTkButton(
            self.sent_btn_frame,
            text=self.gt("sent_clear_btn"),
            width=85,
            height=32,
            fg_color=("gray75", "gray35"),
            hover_color=("gray65", "gray45"),
            command=self.clear_sentence_inputs
        )
        self.sent_clear_btn.pack(side="left")

        self.sent_loading_lbl = ctk.CTkLabel(
            self.sent_btn_frame,
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

        self.sent_confidence_badge = ctk.CTkLabel(
            tgt_lbl_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.sent_confidence_badge.pack(side="left", padx=(12, 0))

        self.sent_copy_btn = ctk.CTkButton(
            tgt_lbl_frame,
            text=self.gt("sent_copy_btn"),
            width=120,
            height=24,
            font=ctk.CTkFont(size=11),
            command=self.copy_sentence_result
        )
        self.sent_copy_btn.pack(side="right")

        self.sent_edit_btn = ctk.CTkButton(
            tgt_lbl_frame,
            text=self.gt("sent_edit_btn"),
            width=140,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color=("gray75", "gray35"),
            hover_color=("gray65", "gray45"),
            command=self.open_correction_dialog,
            state="disabled"
        )
        self.sent_edit_btn.pack(side="right", padx=(0, 8))

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

    # ---------------- WINDOW & SYSTEM TRAY ACTIONS ----------------
    def show_window(self):
        """Brings the window to foreground when clicked from tray or hotkey."""
        self.deiconify()
        self.lift()
        self.focus_force()

    def hide_to_tray(self):
        """Hides the window to tray while keeping background services running."""
        self.withdraw()

    def on_close_requested(self):
        """Handles the window close ('X') action."""
        if self.settings.get("minimize_to_tray", True) or self.settings.get("windows_context_menu", False) or self.settings.get("ctrl_right_click_translate", False):
            self.hide_to_tray()
        else:
            self.quit_app()

    def open_settings_window(self):
        """Opens dedicated Settings Window."""
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self, self.settings)
        else:
            self.settings_window.focus()

    def quit_app(self):
        """Completely terminates application and all background threads."""
        if hasattr(self, "tray") and self.tray:
            self.tray.stop()
        if hasattr(self, "quick_service") and self.quick_service:
            self.quick_service.stop()
        if hasattr(self, "db") and self.db:
            self.db.close()
        if hasattr(self, "syntax_translator") and self.syntax_translator:
            if hasattr(self.syntax_translator, "conn") and self.syntax_translator.conn:
                self.syntax_translator.conn.close()
        self.destroy()
        sys.exit(0)

    # ---------------- CONTEXT MENUS & POPUPS ----------------
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

    def dismiss_quick_button(self):
        try:
            if hasattr(self, "current_quick_btn") and self.current_quick_btn and self.current_quick_btn.winfo_exists():
                self.current_quick_btn.destroy()
                self.current_quick_btn = None
        except Exception:
            pass

    def show_quick_button(self, text: str, x: int, y: int):
        try:
            self.dismiss_quick_button()
            lang = self.settings.get("language", "tr")
            words = text.split()
            if len(words) == 1 and len(text) <= 16 and "\n" not in text:
                btn_txt = f"⚡ Çevir: \"{text}\"" if lang == "tr" else f"⚡ Translate: \"{text}\""
            else:
                btn_txt = "⚡ LocalDictionary ile Çevir" if lang == "tr" else "⚡ Translate with LocalDictionary"
            self.current_quick_btn = QuickTranslateButton(
                self, text, x, y,
                on_translate=self.do_translate_and_show_popup,
                button_text=btn_txt
            )
        except Exception as e:
            print(f"Hızlı buton hatası: {e}")

    def do_translate_and_show_popup(self, text: str, x: int, y: int):
        show_slang = self.settings.get("show_slang_profanity", True)
        words = text.split()
        if len(words) <= 3:
            results, _, _ = self.db.search(text, limit=3, show_slang_profanity=show_slang)
            if results:
                trans = results[0]["target"]
            else:
                res_sent = self.sentence_translator.translate(text, show_slang_profanity=show_slang)
                trans = res_sent.get("translated_text", text)
        else:
            res_sent = self.sentence_translator.translate(text, show_slang_profanity=show_slang)
            trans = res_sent.get("translated_text", text)
        self.show_quick_popup(text, trans, x, y)

    def send_to_sentence(self, text: str):
        self.tabview.set(self.tab_sentence_name)
        self.sent_input.delete("0.0", "end")
        self.sent_input.delete("1.0", "end")
        self.sent_input.insert("0.0", text)
        self.start_sentence_translation()

    # ---------------- SENTENCE TRANSLATION ACTIONS ----------------
    def apply_sent_suggestion(self):
        sugg = self.sent_suggestion_btn.cget("text")
        if sugg:
            self.sent_suggestion_frame.pack_forget()
            self.sent_input.delete("0.0", "end")
            self.sent_input.delete("1.0", "end")
            self.sent_input.insert("0.0", sugg)
            self.start_sentence_translation()

    def clear_sentence_inputs(self):
        self.sent_suggestion_frame.pack_forget()
        self.sent_input.delete("0.0", "end")
        self.sent_input.delete("1.0", "end")
        
        self.sent_output.configure(state="normal")
        self.sent_output.delete("0.0", "end")
        self.sent_output.delete("1.0", "end")
        self.sent_output.configure(state="disabled")

        if hasattr(self, "sent_confidence_badge"):
            self.sent_confidence_badge.configure(text="")
        if hasattr(self, "sent_edit_btn"):
            self.sent_edit_btn.configure(state="disabled")

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
            self.sent_suggestion_frame.pack_forget()
            return

        choice = self.sent_dir_selector.get()
        if choice in ("İngilizce ➔ Türkçe", "English ➔ Turkish"):
            from_l, to_l = "en", "tr"
            dir_code = "en_tr"
        elif choice in ("Türkçe ➔ İngilizce", "Turkish ➔ English"):
            from_l, to_l = "tr", "en"
            dir_code = "tr_en"
        else:
            from_l, to_l = "auto", "auto"
            dir_code = "auto"

        self._last_translation_source = text
        self._last_translation_from = from_l
        self._last_translation_to = to_l

        # Check spelling / typo suggestion
        try:
            sugg = self.spell_checker.get_sentence_suggestion(text, from_lang=from_l)
            if sugg and sugg.strip().lower() != text.strip().lower():
                self.sent_suggestion_lbl.configure(text=self.gt("sent_did_you_mean"))
                self.sent_suggestion_btn.configure(text=sugg)
                self.sent_suggestion_frame.pack(fill="x", padx=6, pady=(0, 6), before=self.sent_btn_frame)
            else:
                self.sent_suggestion_frame.pack_forget()
        except Exception as e:
            print(f"[SpellChecker sentence error]: {e}")
            self.sent_suggestion_frame.pack_forget()

        show_slang = self.settings.get("show_slang_profanity", True)
        loading_text = "Çevriliyor... (Nöral AI)" if self.settings.get("language") == "tr" else "Translating... (Neural AI)"
        self.sent_loading_lbl.configure(text=loading_text)
        self.translate_action_btn.configure(state="disabled")

        def _worker():
            try:
                res = self.sentence_translator.translate(
                    text, from_lang=from_l, to_lang=to_l, show_slang_profanity=show_slang
                )
            except Exception as e:
                print(f"[Translation Worker Error]: {e}")
                res = self.syntax_translator.translate(
                    text, direction=dir_code, show_slang_profanity=show_slang
                )

            def _update_ui():
                self.sent_output.configure(state="normal")
                self.sent_output.delete("0.0", "end")
                self.sent_output.delete("1.0", "end")
                self.sent_output.insert("0.0", res["translated_text"])
                self.sent_output.configure(state="disabled")

                for item in self.breakdown_tree.get_children():
                    self.breakdown_tree.delete(item)

                self._last_breakdown = res.get("breakdown", [])
                cur_lang = self.settings.get("language", "tr")
                for b in self._last_breakdown:
                    alts_str = ", ".join(b.get("alternatives", []))
                    norm_role = normalize_role(b.get("role", ""), lang=cur_lang)
                    norm_pos = normalize_pos(b.get("pos", ""), lang=cur_lang)
                    self.breakdown_tree.insert("", "end", values=(
                        b.get("original", ""),
                        norm_role,
                        norm_pos,
                        b.get("translated", ""),
                        alts_str
                    ))

                # Update confidence badge & enable correction teaching
                score = res.get("confidence", 80)
                level = res.get("confidence_level", "high")
                engine = res.get("engine", "")

                if engine == "user_correction" or score >= 100:
                    badge_text = self.gt("conf_user")
                    badge_color = ("#2e7d32", "#66bb6a")
                elif level == "high" or score >= 80:
                    badge_text = self.gt("conf_high").format(score=score)
                    badge_color = ("#2e7d32", "#66bb6a")
                elif level == "medium" or score >= 55:
                    badge_text = self.gt("conf_med").format(score=score)
                    badge_color = ("#e65100", "#ffa726")
                else:
                    badge_text = self.gt("conf_low").format(score=score)
                    badge_color = ("#c62828", "#ef5350")

                if hasattr(self, "sent_confidence_badge"):
                    self.sent_confidence_badge.configure(text=badge_text, text_color=badge_color)
                if hasattr(self, "sent_edit_btn"):
                    self.sent_edit_btn.configure(state="normal")

                done_text = self.gt("sent_loading_done")
                self.sent_loading_lbl.configure(text=done_text)
                self.translate_action_btn.configure(state="normal")
                self.status_left.configure(text=self.gt("sent_status_ready"))

            self.after(0, _update_ui)

        threading.Thread(target=_worker, daemon=True).start()

    def open_glossary_window(self):
        """Opens dedicated Custom Glossary (Özel Terim Sözlüğü) Window."""
        if self.glossary_window is None or not self.glossary_window.winfo_exists():
            self.glossary_window = GlossaryWindow(self, self.sentence_translator.user_data, self.settings)
        else:
            self.glossary_window.focus()

    def open_correction_dialog(self):
        """Opens modal dialog to correct and teach translation to local AI."""
        current_trans = self.sent_output.get("1.0", "end").strip()
        if not self._last_translation_source or not current_trans:
            return
        if self.correction_dialog is None or not self.correction_dialog.winfo_exists():
            self.correction_dialog = CorrectionDialog(
                self,
                source_text=self._last_translation_source,
                current_translation=current_trans,
                from_lang=self._last_translation_from,
                to_lang=self._last_translation_to,
                on_save_callback=self.on_correction_saved,
                settings_mgr=self.settings
            )
        else:
            self.correction_dialog.focus()

    def on_correction_saved(self, corrected_text: str):
        """Callback when user saves a correction in CorrectionDialog."""
        self.sent_output.configure(state="normal")
        self.sent_output.delete("0.0", "end")
        self.sent_output.delete("1.0", "end")
        self.sent_output.insert("0.0", corrected_text)
        self.sent_output.configure(state="disabled")
        if hasattr(self, "sent_confidence_badge"):
            self.sent_confidence_badge.configure(
                text=self.gt("conf_user"),
                text_color=("#2e7d32", "#66bb6a")
            )


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

    def apply_dict_suggestion(self):
        sugg = self.dict_suggestion_btn.cget("text")
        if sugg:
            self.dict_suggestion_frame.pack_forget()
            self.search_entry.delete(0, "end")
            self.search_entry.insert(0, sugg)
            self.perform_search(sugg)

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.search_entry.focus()
        self.clear_results()
        self.status_left.configure(text=self.gt("status_ready"))

    def clear_results(self):
        if hasattr(self, "dict_suggestion_frame"):
            self.dict_suggestion_frame.pack_forget()
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

        show_slang = self.settings.get("show_slang_profanity", True)
        results, elapsed_ms, detected_dir = self.db.search(query, mode=mode, limit=100, show_slang_profanity=show_slang)
        
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

        # Check spelling suggestion if no exact match
        sugg = None
        if len(query) >= 3:
            exact_match = any(r["source"].lower() == query.lower() for r in results)
            if not exact_match:
                is_en = (detected_dir == "en_tr")
                try:
                    sugg = self.spell_checker.get_word_suggestion(query, is_en=is_en)
                except Exception as e:
                    print(f"[SpellChecker dict error]: {e}")

        if sugg and sugg.lower() != query.lower():
            self.dict_suggestion_lbl.configure(text=self.gt("did_you_mean"))
            self.dict_suggestion_btn.configure(text=sugg)
            self.dict_suggestion_frame.pack(fill="x", padx=4, pady=(0, 6), before=self.content_frame)
        else:
            if hasattr(self, "dict_suggestion_frame"):
                self.dict_suggestion_frame.pack_forget()

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

    def apply_language(self):
        """Dynamically re-labels all GUI elements to the selected language."""
        # 1. Update Tabs (Only 2 tabs!)
        old_dict = self.tab_dict_name
        old_sent = self.tab_sentence_name

        new_dict = self.gt("tab_dict")
        new_sent = self.gt("tab_sentence")

        if old_dict != new_dict:
            self.tabview.rename(old_dict, new_dict)
            self.tab_dict_name = new_dict
        if old_sent != new_sent:
            self.tabview.rename(old_sent, new_sent)
            self.tab_sentence_name = new_sent

        # 2. Header & Window Title
        is_tr = self.settings.get("language", "tr") == "tr"
        badge_txt = "Açık Kaynak (BETA)" if is_tr else "Open Source (BETA)"
        self.title(f"LocalDictionary v1.41 - {badge_txt}")
        self.title_label.configure(text=self.gt("app_title"))
        self.sub_label.configure(text=self.gt("app_subtitle"))
        self.settings_btn.configure(text=self.gt("settings_btn"))
        self.history_btn.configure(text=self.gt("history_btn"))

        # 3. Dictionary Tab
        self.dict_dir_lbl.configure(text=self.gt("search_dir_lbl"))
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
        if hasattr(self, "sent_glossary_btn"):
            self.sent_glossary_btn.configure(text=self.gt("btn_glossary"))
        if hasattr(self, "sent_edit_btn"):
            self.sent_edit_btn.configure(text=self.gt("sent_edit_btn"))
        self.sent_output_lbl.configure(text=self.gt("sent_status_ready"))
        if hasattr(self, "sent_loading_lbl") and self.sent_loading_lbl.cget("text"):
            self.sent_loading_lbl.configure(text=self.gt("sent_loading_done"))
        self.breakdown_lbl.configure(text=self.gt("breakdown_title"))
        self.breakdown_tree.heading("original", text=self.gt("col_orig"))
        self.breakdown_tree.heading("role", text=self.gt("col_role"))
        self.breakdown_tree.heading("pos", text=self.gt("col_pos"))
        self.breakdown_tree.heading("translated", text=self.gt("col_trans"))
        self.breakdown_tree.heading("alts", text=self.gt("col_alts"))

        # Re-populate breakdown tree with new language if analysis exists
        if hasattr(self, "_last_breakdown") and self._last_breakdown:
            for item in self.breakdown_tree.get_children():
                self.breakdown_tree.delete(item)
            cur_lang = self.settings.get("language", "tr")
            for b in self._last_breakdown:
                alts_str = ", ".join(b.get("alternatives", []))
                norm_role = normalize_role(b.get("role", ""), lang=cur_lang)
                norm_pos = normalize_pos(b.get("pos", ""), lang=cur_lang)
                self.breakdown_tree.insert("", "end", values=(
                    b.get("original", ""),
                    norm_role,
                    norm_pos,
                    b.get("translated", ""),
                    alts_str
                ))

        # 5. Status Bar
        self.status_right.configure(text=self.gt("status_engine_badge"))
        self.status_left.configure(text=self.gt("status_ready"))

        # 6. Tray Icon Localization
        if hasattr(self, "tray") and self.tray:
            self.tray.update_language()

    def destroy(self):
        if hasattr(self, "debounce_timer") and self.debounce_timer:
            try:
                self.after_cancel(self.debounce_timer)
            except Exception:
                pass
        if hasattr(self, "tray") and self.tray:
            self.tray.stop()
        if hasattr(self, "quick_service") and self.quick_service:
            self.quick_service.stop()
        if hasattr(self, "db") and self.db:
            self.db.close()
        if hasattr(self, "syntax_translator") and self.syntax_translator:
            if hasattr(self.syntax_translator, "conn") and self.syntax_translator.conn:
                self.syntax_translator.conn.close()
        super().destroy()


def run_app():
    start_min = "--minimized" in sys.argv
    app = TranslatorApp(start_minimized=start_min)
    app.mainloop()

if __name__ == "__main__":
    run_app()

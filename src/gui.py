import sys
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Optional
from src.db import DictionaryDB
from src.history import HistoryManager

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
        # Header
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=16, pady=(14, 8))

        lbl = ctk.CTkLabel(top_frame, text="🕒 Arama Geçmişi", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(side="left")

        # Treeview for history
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

        # Buttons
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
        self.geometry("980x700")
        self.minsize(780, 540)

        # Initialize Database & History
        try:
            self.db = DictionaryDB()
        except Exception as e:
            self.show_fatal_error(str(e))
            return

        self.history = HistoryManager()
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
            text="v1.1 (100% Çevrimdışı)", 
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

        # Direction Mode (Segmented Button)
        self.dir_selector = ctk.CTkSegmentedButton(
            self.header_frame,
            values=["Otomatik", "EN ➔ TR", "TR ➔ EN"],
            command=lambda val: self.on_search_change()
        )
        self.dir_selector.set("Otomatik")
        self.dir_selector.pack(side="right", padx=15, pady=12)

        # 2. Search Box Frame
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=18, pady=(14, 4))

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Kelime veya deyim yazın... (Örn: computer, başarı, serendipity, break)",
            height=42,
            font=ctk.CTkFont(size=15)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_key_release)
        self.search_entry.bind("<Return>", lambda e: self.perform_search(self.search_entry.get()))

        self.clear_btn = ctk.CTkButton(
            self.search_frame,
            text="✕",
            width=42,
            height=42,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=self.clear_search
        )
        self.clear_btn.pack(side="left", padx=(0, 10))

        self.search_btn = ctk.CTkButton(
            self.search_frame,
            text="Ara",
            width=80,
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self.perform_search(self.search_entry.get())
        )
        self.search_btn.pack(side="left")

        # 2.5 Quick History Chips Frame
        self.quick_history_frame = ctk.CTkFrame(self, fg_color="transparent", height=28)
        self.quick_history_frame.pack(fill="x", padx=18, pady=(2, 8))
        self.quick_history_frame.pack_propagate(False)

        # 3. Main Paned Content
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=18, pady=0)

        # Treeview for results (high performance list)
        self.tree_frame = ctk.CTkFrame(self.content_frame)
        self.tree_frame.pack(fill="both", expand=True, pady=(0, 10))

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

        # Scrollbar for treeview
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_row_selected)
        self.tree.bind("<Double-1>", self.copy_selected_translation)

        # 4. Detail / Definition Box
        self.detail_frame = ctk.CTkFrame(self.content_frame, height=135)
        self.detail_frame.pack(fill="x", pady=(0, 10))
        self.detail_frame.pack_propagate(False)

        self.detail_header = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        self.detail_header.pack(fill="x", padx=12, pady=(6, 4))

        self.detail_title = ctk.CTkLabel(
            self.detail_header, 
            text="Sözlük Tanımı & Bilgi", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.detail_title.pack(side="left")

        self.copy_btn = ctk.CTkButton(
            self.detail_header,
            text="Çeviriyi Kopyala",
            width=110,
            height=26,
            font=ctk.CTkFont(size=12),
            command=self.copy_selected_translation
        )
        self.copy_btn.pack(side="right")

        self.detail_text = ctk.CTkTextbox(
            self.detail_frame, 
            wrap="word", 
            font=ctk.CTkFont(size=13),
            activate_scrollbars=True
        )
        self.detail_text.pack(fill="both", expand=True, padx=12, pady=(0, 6))
        self.detail_text.configure(state="disabled")

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
            text="● 1.7 Milyon+ Kayıt (100% Çevrimdışı - B-Tree İndeksli)", 
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50"
        )
        self.status_right.pack(side="right", padx=18)

    def update_quick_history(self):
        """Update recent search chips under search bar."""
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

        style.configure(
            "Treeview",
            background=bg,
            foreground=fg,
            fieldbackground=field_bg,
            rowheight=26,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.map("Treeview", background=[("selected", sel_bg)], foreground=[("selected", sel_fg)])
        
        style.configure(
            "Treeview.Heading",
            background=heading_bg,
            foreground=heading_fg,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=4
        )
        style.map("Treeview.Heading", background=[("active", heading_bg)])

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
        
        # Populate Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.current_results = results
        for r in results:
            self.tree.insert("", "end", values=(r["source"], r["type"], r["category"], r["target"]))

        # Select first row if exists
        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self.on_row_selected(None)
            
            # Save to persistent history
            if save_to_history and len(query) >= 2:
                self.history.add_search(query, detected_dir, len(results))
                self.update_quick_history()
        else:
            self.show_no_results(query)

        self.status_left.configure(text=f"{len(results)} sonuç bulundu ({elapsed_ms:.1f} ms) — Yön: {detected_dir}")

    def show_no_results(self, query: str):
        self.set_detail_text(f"'{query}' kelimesi için doğrudan eşleşme bulunamadı.\n\nİpucu: Yazımı kontrol edebilir veya kelimenin kök halini aratabilirsiniz.")

    def on_row_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0], "values")
        if not values:
            return

        source, wtype, category, target = values
        detail_lines = [f"【{source}】 ➔ {target} ({wtype} - {category})", ""]
        
        # TDK Turkish definitions
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

        # Webster English definitions
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
        super().destroy()

def run_app():
    app = TranslatorApp()
    app.mainloop()

if __name__ == "__main__":
    run_app()

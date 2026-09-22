import os
import sys
import time
import threading
import tkinter as tk
from tkinter import Menu
import customtkinter as ctk
from typing import Optional, Callable

# Windows API for global hotkeys & mouse detection
try:
    import ctypes
    user32 = ctypes.windll.user32
    VK_CONTROL = 0x11
    VK_RBUTTON = 0x02
    HAS_USER32 = True
except Exception:
    HAS_USER32 = False

class QuickTranslatePopup(ctk.CTkToplevel):
    """
    Modern floating translation popup card positioned near cursor.
    """
    def __init__(self, master, source_text: str, translated_text: str, x: int, y: int, on_open_in_dict: Optional[Callable[[str], None]] = None):
        super().__init__(master)
        
        self.on_open_in_dict = on_open_in_dict
        self.source_text = source_text.strip()
        self.translated_text = translated_text.strip()

        # Frameless, topmost window
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Style frame
        self.card = ctk.CTkFrame(
            self, 
            corner_radius=10, 
            border_width=2, 
            border_color=("gray60", "#3a7eb8"),
            fg_color=("gray95", "#232323")
        )
        self.card.pack(fill="both", expand=True)

        # Header bar
        header = ctk.CTkFrame(self.card, fg_color="transparent", height=24)
        header.pack(fill="x", padx=8, pady=(6, 2))

        lbl_title = ctk.CTkLabel(
            header, 
            text="⚡ Hızlı Çeviri / Quick Translate", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray20", "#64B5F6")
        )
        lbl_title.pack(side="left")

        btn_close = ctk.CTkButton(
            header,
            text="✕",
            width=20,
            height=20,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            text_color="gray",
            hover_color=("gray80", "gray35"),
            command=self.destroy
        )
        btn_close.pack(side="right")

        # Source snippet
        src_display = self.source_text if len(self.source_text) <= 80 else self.source_text[:77] + "..."
        lbl_src = ctk.CTkLabel(
            self.card,
            text=f"❝ {src_display} ❞",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color=("gray40", "gray70"),
            wraplength=340,
            justify="left"
        )
        lbl_src.pack(fill="x", padx=12, pady=(2, 4), anchor="w")

        # Translation result
        lbl_trans = ctk.CTkLabel(
            self.card,
            text=self.translated_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("black", "white"),
            wraplength=340,
            justify="left"
        )
        lbl_trans.pack(fill="x", padx=12, pady=(2, 8), anchor="w")

        # Action buttons
        btn_bar = ctk.CTkFrame(self.card, fg_color="transparent")
        btn_bar.pack(fill="x", padx=10, pady=(0, 8))

        btn_copy = ctk.CTkButton(
            btn_bar,
            text="📋 Kopyala",
            width=80,
            height=24,
            font=ctk.CTkFont(size=11),
            command=self.copy_and_close
        )
        btn_copy.pack(side="left", padx=(0, 6))

        if self.on_open_in_dict:
            btn_open = ctk.CTkButton(
                btn_bar,
                text="🔍 Sözlükte Aç",
                width=100,
                height=24,
                font=ctk.CTkFont(size=11),
                fg_color=("gray75", "gray30"),
                hover_color=("gray65", "gray40"),
                command=self.open_dict_and_close
            )
            btn_open.pack(side="left")

        # Calculate position on screen
        self.update_idletasks()
        w = max(self.winfo_reqwidth(), 320)
        h = max(self.winfo_reqheight(), 120)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        pos_x = min(x + 12, screen_w - w - 15)
        pos_y = min(y + 12, screen_h - h - 15)
        self.geometry(f"{w}x{h}+{pos_x}+{pos_y}")

        # Auto-dismiss on click outside or after 8 seconds
        self.after(8000, self.safe_destroy)
        self.bind("<FocusOut>", lambda e: self.safe_destroy())

    def safe_destroy(self):
        try:
            if self.winfo_exists():
                self.destroy()
        except Exception:
            pass

    def copy_and_close(self):
        self.clipboard_clear()
        self.clipboard_append(self.translated_text)
        self.safe_destroy()

    def open_dict_and_close(self):
        if self.on_open_in_dict:
            self.on_open_in_dict(self.source_text)
        self.safe_destroy()


class GlobalQuickTranslateService:
    """
    Lightweight background listener for Ctrl + Right-Click global text translation.
    """
    def __init__(self, app, settings_mgr, db, syntax_translator):
        self.app = app
        self.settings = settings_mgr
        self.db = db
        self.syntax_translator = syntax_translator
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        if not HAS_USER32 or self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _monitor_loop(self):
        last_trigger_time = 0
        while self.running:
            try:
                time.sleep(0.04) # low CPU usage (40ms polling)
                if not self.settings.get("right_click_translate", True):
                    time.sleep(0.3)
                    continue

                trigger = self.settings.get("right_click_trigger", "ctrl_right_click")
                if trigger == "ctrl_right_click":
                    ctrl_down = bool(user32.GetAsyncKeyState(VK_CONTROL) & 0x8000)
                    rbutton_down = bool(user32.GetAsyncKeyState(VK_RBUTTON) & 0x8000)
                    
                    if ctrl_down and rbutton_down:
                        now = time.time()
                        if now - last_trigger_time > 0.8: # debounce 800ms
                            last_trigger_time = now
                            self._trigger_translation()
            except Exception:
                time.sleep(0.5)

    def _trigger_translation(self):
        # 1. Get cursor position
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        cur_x, cur_y = pt.x, pt.y

        # 2. Simulate Ctrl+C to copy selected text to clipboard
        # Save previous clipboard
        prev_clip = ""
        try:
            prev_clip = self.app.clipboard_get()
        except Exception:
            pass

        # Send Ctrl+C
        # VK_CONTROL = 0x11, 'C' = 0x43, KEYEVENTF_KEYUP = 0x0002
        user32.keybd_event(0x43, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(0x43, 0, 0x0002, 0)
        time.sleep(0.08)

        new_clip = ""
        try:
            new_clip = self.app.clipboard_get()
        except Exception:
            pass

        if not new_clip or new_clip == prev_clip or len(new_clip.strip()) < 1 or len(new_clip.strip()) > 3000:
            return

        text = new_clip.strip()
        
        # 3. Translate text
        # If single word / short phrase (up to 3 words), query dictionary
        words = text.split()
        if len(words) <= 3:
            results, _, _ = self.db.search(text, limit=3)
            if results:
                trans = results[0]["target"]
            else:
                res_sent = self.syntax_translator.translate(text, direction="auto")
                trans = res_sent.get("translated_text", text)
        else:
            res_sent = self.syntax_translator.translate(text, direction="auto")
            trans = res_sent.get("translated_text", text)

        # 4. Show popup in main GUI thread
        self.app.after(0, lambda: self.app.show_quick_popup(text, trans, cur_x, cur_y))


def attach_context_menu(widget, on_search: Optional[Callable[[str], None]] = None, on_sentence: Optional[Callable[[str], None]] = None, get_text_fn: Optional[Callable[[str], str]] = None):
    """
    Attaches a right-click context menu to entries, textboxes, or labels.
    """
    def show_menu(event):
        try:
            menu = Menu(widget, tearoff=0)
            
            # Check if text is selected
            selected_text = ""
            try:
                selected_text = widget.selection_get().strip()
            except Exception:
                pass

            gt = get_text_fn or (lambda k: k)

            if selected_text:
                if on_search:
                    menu.add_command(
                        label=f"{gt('ctx_search_dict')} ('{selected_text[:15]}...')", 
                        command=lambda: on_search(selected_text)
                    )
                if on_sentence:
                    menu.add_command(
                        label=f"{gt('ctx_send_sentence')}", 
                        command=lambda: on_sentence(selected_text)
                    )
                menu.add_separator()
                menu.add_command(
                    label=gt("ctx_copy"), 
                    command=lambda: (widget.clipboard_clear(), widget.clipboard_append(selected_text))
                )
            else:
                # If widget supports standard paste/cut
                if hasattr(widget, "insert") and hasattr(widget, "delete"):
                    menu.add_command(
                        label=gt("ctx_paste"),
                        command=lambda: widget.event_generate("<<Paste>>")
                    )
                    menu.add_command(
                        label=gt("ctx_copy"),
                        command=lambda: widget.event_generate("<<Copy>>")
                    )

            menu.tk_popup(event.x_root, event.y_root)
        except Exception:
            pass

    widget.bind("<Button-3>", show_menu)

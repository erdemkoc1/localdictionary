import os
import sys
import time
import threading
import tkinter as tk
from tkinter import Menu
import customtkinter as ctk
from typing import Optional, Callable

# Windows API for global hotkeys, mouse detection & clipboard
try:
    import ctypes
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    
    CF_UNICODETEXT = 13
    VK_LBUTTON = 0x01
    VK_RBUTTON = 0x02
    VK_CONTROL = 0x11
    VK_C = 0x43
    KEYEVENTF_KEYUP = 0x0002

    # Set explicit 64-bit Win32 prototypes
    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
    user32.OpenClipboard.restype = ctypes.c_bool
    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = ctypes.c_bool
    user32.GetClipboardData.argtypes = [ctypes.c_uint]
    user32.GetClipboardData.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.restype = ctypes.c_bool

    HAS_USER32 = True
except Exception:
    HAS_USER32 = False


def get_clipboard_text_win32() -> str:
    """Thread-safe and fast direct Win32 Unicode clipboard reader."""
    if not HAS_USER32 or not user32.OpenClipboard(None):
        return ""
    try:
        h_mem = user32.GetClipboardData(CF_UNICODETEXT)
        if not h_mem:
            return ""
        p_mem = kernel32.GlobalLock(h_mem)
        if not p_mem:
            return ""
        try:
            return ctypes.c_wchar_p(p_mem).value or ""
        finally:
            kernel32.GlobalUnlock(h_mem)
    except Exception:
        return ""
    finally:
        user32.CloseClipboard()


def send_ctrl_c():
    """Simulates Ctrl + C reliably ensuring VK_CONTROL is held down."""
    ctrl_was_down = bool(user32.GetAsyncKeyState(VK_CONTROL) & 0x8000)
    if not ctrl_was_down:
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        time.sleep(0.015)
    
    user32.keybd_event(VK_C, 0, 0, 0)
    time.sleep(0.02)
    user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.015)
    
    if not ctrl_was_down:
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


class QuickTranslateButton(ctk.CTkToplevel):
    """
    Floating pill badge [ ⚡ Çevir / LocalDictionary ]
    displayed near cursor when user selects text or right-clicks in any application
    (Brave, Chrome, Firefox, Edge, Word, PDF, Notepad, etc.).
    """
    def __init__(self, master, text: str, x: int, y: int, on_translate: Callable[[str, int, int], None], button_text: Optional[str] = None):
        super().__init__(master)
        self.text = text.strip()
        self.on_translate = on_translate
        self.click_x = x
        self.click_y = y

        self.overrideredirect(True)
        self.attributes("-topmost", True)

        if not button_text:
            button_text = "⚡ LocalDictionary ile Çevir"

        self.card = ctk.CTkFrame(
            self,
            corner_radius=16,
            border_width=1,
            border_color="#64B5F6",
            fg_color="#1F538D"
        )
        self.card.pack(fill="both", expand=True)

        self.btn = ctk.CTkButton(
            self.card,
            text=button_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#1F538D",
            hover_color="#1565C0",
            text_color="white",
            corner_radius=16,
            height=30,
            command=self.on_click
        )
        self.btn.pack(side="left", padx=(8, 2), pady=3)

        self.btn_close = ctk.CTkButton(
            self.card,
            text="✕",
            width=22,
            height=22,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color="#0D47A1",
            text_color="#BBDEFB",
            command=self.safe_destroy
        )
        self.btn_close.pack(side="right", padx=(0, 6), pady=3)

        self.bind("<Escape>", lambda e: self.safe_destroy())

        self.update_idletasks()
        w = max(self.winfo_reqwidth(), 160)
        h = max(self.winfo_reqheight(), 36)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        pos_x = min(max(x - 20, 10), screen_w - w - 10)
        pos_y = max(y - 44, 10) if y - 44 > 0 else min(y + 24, screen_h - h - 10)
        self.geometry(f"{w}x{h}+{pos_x}+{pos_y}")

        # Auto-dismiss after 4.5 seconds
        self.after(4500, self.safe_destroy)

    def on_click(self):
        self.safe_destroy()
        if self.on_translate:
            self.on_translate(self.text, self.click_x, self.click_y)

    def safe_destroy(self):
        try:
            if self.winfo_exists():
                self.destroy()
        except Exception:
            pass


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
    Ultra-reliable background listener for:
    1. Text selection in browsers & apps (Brave, Chrome, Firefox, Word, PDF)
    2. Right-click on selected text
    3. Ctrl + Right-click instant translation
    """
    def __init__(self, app, settings_mgr, db, syntax_translator):
        self.app = app
        self.settings = settings_mgr
        self.db = db
        self.syntax_translator = syntax_translator
        self.running = False
        self.thread: Optional[threading.Thread] = None

        self.last_trigger_time = 0.0
        self.lbutton_is_down = False
        self.lbutton_down_pos = (0, 0)
        self.lbutton_down_time = 0.0
        self.last_lbutton_up_time = 0.0
        self.last_lbutton_up_pos = (0, 0)
        self.rbutton_is_down = False

    def start(self):
        if not HAS_USER32 or self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _is_inside_own_window(self, cx: int, cy: int) -> bool:
        """Checks if cursor is currently within LocalDictionary's own windows."""
        try:
            # Main window
            if self.app.winfo_viewable():
                wx, wy = self.app.winfo_rootx(), self.app.winfo_rooty()
                ww, wh = self.app.winfo_width(), self.app.winfo_height()
                if wx <= cx <= wx + ww and wy <= cy <= wy + wh:
                    return True
            # Settings window
            if hasattr(self.app, "settings_window") and self.app.settings_window and self.app.settings_window.winfo_exists():
                sw = self.app.settings_window
                if sw.winfo_viewable():
                    sx, sy = sw.winfo_rootx(), sw.winfo_rooty()
                    if sx <= cx <= sx + sw.winfo_width() and sy <= cy <= sy + sw.winfo_height():
                        return True
            # Quick popup
            if hasattr(self.app, "current_popup") and self.app.current_popup and self.app.current_popup.winfo_exists():
                qp = self.app.current_popup
                if qp.winfo_viewable():
                    qx, qy = qp.winfo_rootx(), qp.winfo_rooty()
                    if qx <= cx <= qx + qp.winfo_width() and qy <= cy <= qy + qp.winfo_height():
                        return True
        except Exception:
            pass
        return False

    def _is_inside_quick_button(self, cx: int, cy: int) -> bool:
        """Checks if cursor is currently clicking on the floating quick button."""
        try:
            if hasattr(self.app, "current_quick_btn") and self.app.current_quick_btn and self.app.current_quick_btn.winfo_exists():
                qb = self.app.current_quick_btn
                if qb.winfo_viewable():
                    bx = qb.winfo_rootx()
                    by = qb.winfo_rooty()
                    bw = qb.winfo_width()
                    bh = qb.winfo_height()
                    if bx <= cx <= bx + bw and by <= cy <= by + bh:
                        return True
        except Exception:
            pass
        return False

    def _monitor_loop(self):
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        pt = POINT()

        while self.running:
            try:
                time.sleep(0.03)  # 30ms sleep (very low CPU usage)

                ctrl_rc_enabled = self.settings.get("ctrl_right_click_translate", True)
                rc_btn_enabled = self.settings.get("right_click_translate", True) or self.settings.get("windows_context_menu", True)
                sel_enabled = self.settings.get("selection_translate", True)
                dbl_enabled = self.settings.get("double_click_translate", False)

                if not (ctrl_rc_enabled or rc_btn_enabled or sel_enabled or dbl_enabled):
                    time.sleep(0.3)
                    continue

                user32.GetCursorPos(ctypes.byref(pt))
                cx, cy = pt.x, pt.y

                l_down = bool(user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000)
                r_down = bool(user32.GetAsyncKeyState(VK_RBUTTON) & 0x8000)
                ctrl_down = bool(user32.GetAsyncKeyState(VK_CONTROL) & 0x8000)

                now = time.time()

                # Don't trigger if cursor is inside LocalDictionary's own windows
                if self._is_inside_own_window(cx, cy):
                    self.lbutton_is_down = l_down
                    self.rbutton_is_down = r_down
                    continue

                # --- 1. Left Mouse Button Gestures (Text Selection & Double Click) ---
                if l_down and not self.lbutton_is_down:
                    self.lbutton_is_down = True
                    self.lbutton_down_pos = (cx, cy)
                    self.lbutton_down_time = now

                    # If clicking elsewhere on screen, dismiss any lingering quick button
                    if not self._is_inside_quick_button(cx, cy):
                        self.app.after(0, self.app.dismiss_quick_button)

                elif not l_down and self.lbutton_is_down:
                    self.lbutton_is_down = False
                    up_time = now
                    down_x, down_y = self.lbutton_down_pos
                    dist = ((cx - down_x) ** 2 + (cy - down_y) ** 2) ** 0.5
                    duration = up_time - self.lbutton_down_time

                    # Drag selection: moved >= 8 pixels with reasonable gesture speed
                    is_drag = (dist >= 8 and 0.08 < duration < 4.0)

                    # Double click selection: two quick clicks (<450ms) at same spot
                    is_double_click = False
                    if dist < 6:
                        dt_last_up = up_time - self.last_lbutton_up_time
                        last_up_x, last_up_y = self.last_lbutton_up_pos
                        dist_last = ((cx - last_up_x) ** 2 + (cy - last_up_y) ** 2) ** 0.5
                        if 0.05 < dt_last_up < 0.45 and dist_last < 8:
                            is_double_click = True

                    self.last_lbutton_up_time = up_time
                    self.last_lbutton_up_pos = (cx, cy)

                    should_trigger = (is_drag and sel_enabled) or (is_double_click and dbl_enabled)
                    if should_trigger:
                        if now - self.last_trigger_time > 0.45:
                            time.sleep(0.04)  # brief wait for browser to paint selection
                            self._try_capture_and_show(cx, cy, immediate=False)

                # --- 2. Right Mouse Button (Right-Click & Ctrl + Right-Click) ---
                if r_down and not self.rbutton_is_down:
                    self.rbutton_is_down = True
                    if now - self.last_trigger_time > 0.45:
                        if ctrl_down and ctrl_rc_enabled:
                            self.last_trigger_time = now
                            self._try_capture_and_show(cx, cy, immediate=True)
                        elif not ctrl_down and rc_btn_enabled:
                            self.last_trigger_time = now
                            time.sleep(0.03)  # brief pause for right-click event
                            self._try_capture_and_show(cx, cy, immediate=False)
                elif not r_down and self.rbutton_is_down:
                    self.rbutton_is_down = False

            except Exception:
                time.sleep(0.5)

    def _try_capture_and_show(self, cx: int, cy: int, immediate: bool = False):
        """Attempts to copy selected text via simulated Ctrl+C and verifies sequence number."""
        seq_before = user32.GetClipboardSequenceNumber()

        # Simulate Ctrl+C
        send_ctrl_c()

        # Wait up to 120ms for sequence number to change
        copied = False
        for _ in range(8):
            time.sleep(0.015)
            if user32.GetClipboardSequenceNumber() > seq_before:
                copied = True
                break

        if not copied:
            return

        text = get_clipboard_text_win32().strip()
        if not text or len(text) < 1 or len(text) > 3000:
            return

        self.last_trigger_time = time.time()

        if immediate:
            # Immediate full translation popup (Ctrl + Right Click)
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

            self.app.after(0, lambda: self.app.show_quick_popup(text, trans, cx, cy))
        else:
            # Floating Button [ ⚡ Çevir / LocalDictionary ile Çevir ]
            self.app.after(0, lambda: self.app.show_quick_button(text, cx, cy))


def attach_context_menu(widget, on_search: Optional[Callable[[str], None]] = None, on_sentence: Optional[Callable[[str], None]] = None, get_text_fn: Optional[Callable[[str], str]] = None):
    """
    Attaches a right-click context menu to entries, textboxes, or labels.
    """
    def show_menu(event):
        try:
            menu = Menu(widget, tearoff=0)
            
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

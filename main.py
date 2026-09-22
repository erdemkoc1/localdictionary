import os
import sys
import traceback

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    try:
        from src.gui import run_app
        run_app()
    except Exception as e:
        err_msg = traceback.format_exc()
        try:
            log_path = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "error_log.txt")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(err_msg)
        except Exception:
            pass
        
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("LocalDictionary Başlatma Hatası", f"Uygulama başlatılırken bir hata oluştu:\n\n{e}\n\nAyrıntılar error_log.txt dosyasına kaydedildi.")
        except Exception:
            pass

import sys
import traceback

from src.paths import get_log_dir
from src.single_instance import SingleInstanceGuard
from src.network_guard import enforce_no_network

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    enforce_no_network()
    instance_guard = SingleInstanceGuard()
    try:
        if not instance_guard.acquire():
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("LocalDictionary", "LocalDictionary is already running.")
            root.destroy()
            raise SystemExit(0)

        from src.gui import run_app
        run_app()
    except Exception as e:
        err_msg = traceback.format_exc()
        try:
            log_path = str(get_log_dir() / "error_log.txt")
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
    finally:
        instance_guard.release()

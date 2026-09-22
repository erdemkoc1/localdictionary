import os
import sys
import shutil
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

def build_and_deploy():
    print("=" * 65)
    print("LOCALDICTIONARY - ULTRA STABLE PORTABLE EXE DERLEME")
    print("=" * 65)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    target_name = "localdictionary"
    dist_app_dir = os.path.join(dist_dir, target_name)

    # 1. Run PyInstaller (Clean, lightweight, only customtkinter)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", target_name,
        "--collect-all", "customtkinter",
        "--clean",
        os.path.join(base_dir, "main.py")
    ]

    print("PyInstaller çalıştırılıyor:")
    print(" ".join(cmd))
    res = subprocess.run(cmd, cwd=base_dir)
    if res.returncode != 0:
        print("HATA: PyInstaller derleme başarısız oldu!")
        sys.exit(res.returncode)

    # 2. Copy dictionary.db
    src_db = os.path.join(base_dir, "data", "dictionary.db")
    dest_data_dir = os.path.join(dist_app_dir, "data")
    os.makedirs(dest_data_dir, exist_ok=True)
    
    print("\n1.7M Sözlük veritabanı taşınabilir klasöre ekleniyor...")
    shutil.copy2(src_db, os.path.join(dest_data_dir, "dictionary.db"))
    shutil.copy2(src_db, os.path.join(dist_app_dir, "dictionary.db"))

    # 3. Create README.txt
    readme_content = (
        "LOCALDICTIONARY (TR ⇄ EN) - PORTABLE SÜRÜM\n"
        "===========================================\n\n"
        "Bu uygulama tamamen yerel ve internetsiz çalışır.\n"
        "Kuruluma gerek yoktur.\n\n"
        "Çalıştırmak için 'localdictionary.exe' dosyasına çift tıklayın.\n\n"
        "İçerik:\n"
        "- 1.7 Milyon Kayıtlı Çift Yönlü Sözlük (TDK & Webster Dahil)\n"
        "- Kalıcı Arama Geçmişi (Program kapansa dahi saklanır)\n"
        "- Sentaks ve Kural Tabanlı Cümle Çevirisi (BETA - Anlık & Donanımsız)\n"
        "- Koyu (Dark) ve Açık (Light) Tema Desteği\n"
    )
    with open(os.path.join(dist_app_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    # 4. Copy to Desktop locations
    desktop_targets = [
        os.path.expanduser("~/OneDrive/Masaüstü"),
        os.path.expanduser("~/OneDrive/Desktop"),
        os.path.expanduser("~/Desktop"),
        "/OneDrive/Masaüstü",
        "/Desktop"
    ]
    
    deployed_paths = []
    seen = set()
    for d in desktop_targets:
        norm_d = os.path.normpath(d)
        if os.path.exists(norm_d) and norm_d not in seen:
            seen.add(norm_d)
            dest_folder = os.path.join(norm_d, "localdictionary")
            print(f"\nMasaüstüne kopyalanıyor: {dest_folder}")
            if os.path.exists(dest_folder):
                try:
                    shutil.rmtree(dest_folder)
                except Exception as e:
                    print(f"Eski klasör temizlenirken uyarı: {e}")
            shutil.copytree(dist_app_dir, dest_folder, dirs_exist_ok=True)
            deployed_paths.append(dest_folder)

    print("\n" + "=" * 65)
    print("TAMAMLANDI!")
    print(f"Uygulama Adı: localdictionary.exe")
    print(f"Masaüstü Konumları:")
    for dp in deployed_paths:
        print(f"  -> {dp}\\localdictionary.exe")
    print("=" * 65)

if __name__ == "__main__":
    build_and_deploy()

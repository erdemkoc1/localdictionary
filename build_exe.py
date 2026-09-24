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

    # 1. Run PyInstaller (CustomTkinter, Pystray, PIL, CTranslate2, ArgosTranslate)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", target_name,
        "--collect-all", "customtkinter",
        "--collect-all", "pystray",
        "--collect-all", "PIL",
        "--collect-all", "ctranslate2",
        "--collect-all", "argostranslate",
        "--hidden-import", "src.user_data",
        "--hidden-import", "src.clause_splitter",
        "--hidden-import", "src.idiom_engine",
        "--clean",
        os.path.join(base_dir, "main.py")
    ]

    print("PyInstaller çalıştırılıyor:")
    print(" ".join(cmd))
    res = subprocess.run(cmd, cwd=base_dir)
    if res.returncode != 0:
        print("HATA: PyInstaller derleme başarısız oldu!")
        sys.exit(res.returncode)

    # 2. Copy dictionary.db, settings, and NMT models
    src_db = os.path.join(base_dir, "data", "dictionary.db")
    dest_data_dir = os.path.join(dist_app_dir, "data")
    os.makedirs(dest_data_dir, exist_ok=True)
    
    print("\n2.2M+ Sözlük veritabanı taşınabilir klasöre ekleniyor...")
    shutil.copy2(src_db, os.path.join(dest_data_dir, "dictionary.db"))
    shutil.copy2(src_db, os.path.join(dist_app_dir, "dictionary.db"))

    src_settings = os.path.join(base_dir, "data", "settings.json")
    if os.path.exists(src_settings):
        shutil.copy2(src_settings, os.path.join(dest_data_dir, "settings.json"))

    src_models = os.path.join(base_dir, "data", "models")
    dest_models_dir = os.path.join(dest_data_dir, "models")
    if os.path.exists(src_models):
        print("\nNöral Yapay Zeka Çeviri Modelleri (CTranslate2 NMT) taşınabilir klasöre ekleniyor...")
        shutil.copytree(src_models, dest_models_dir, dirs_exist_ok=True)

    # 3. Create README.txt
    readme_content = (
        "LOCALDICTIONARY v1.41 (AÇIK KAYNAK / OPEN SOURCE - BETA)\n"
        "========================================================\n\n"
        "Bu uygulama tamamen yerel ve internetsiz çalışır (100% Offline, Privacy-First).\n"
        "Kuruluma gerek yoktur, sıfır yapılandırma ile çalışır.\n\n"
        "Çalıştırmak için 'localdictionary.exe' dosyasına çift tıklayın.\n\n"
        "İçerik & Özellikler (v1.41 BETA):\n"
        "- 1.68M+ Çift Yönlü Sözlük & 2.2M+ Toplam Kayıt (Wiktionary, TDK, Webster, AWL, GRE)\n"
        "- CEFR A1-C2 Seviye Etiketleme & Öncelikli Anlam Sıralaması (Re-Ranking)\n"
        "- Derin Çok Anlamlılık (Polysemy) ve Genişletilmiş Deyimler Motoru\n"
        "- Çevrimdışı Nöral Makine Çevirisi (CTranslate2 NMT - 100% Yerel AI)\n"
        "- Çeviri Önbelleği (Translation Cache - Alt-milisaniye anında yanıt)\n"
        "- İnsan Odaklı Öğrenme ('Doğrusunu Öğret' - Kullanıcı düzeltmelerini anında öğrenir)\n"
        "- Özel Terim Sözlüğü (Custom Glossary - Tanımlı terim karşılıklarını zorunlu uygular)\n"
        "- Cümle Ayrıştırma (Clause Splitting - Uzun ve bileşik cümleleri akıllı böler)\n"
        "- Dinamik Güven Skoru & Rozetler (Yeşil %80+ / Sarı %55-79 / Kırmızı Uyarı)\n"
        "- Sağ Tık & Hızlı Seçim Çevirisi (Ctrl + Sağ Tık veya Pano İzleme)\n"
        "- Ayarlar: Arayüz Dili (TR/EN), Koyu/Açık Tema, Sağ Tık Yapılandırması\n"
        "- Kalıcı Arama Geçmişi (Program kapansa dahi saklanır)\n"
        "- Argo & Küfür Filtreleme ve Doğal Sokak Dili Desteği\n"
        "- Lisans: Açık Kaynak (MIT / Apache 2.0 / GPL Uyumlu)\n"
    )
    with open(os.path.join(dist_app_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)


    # 4. Copy to Desktop locations
    user_home = os.path.expanduser("~")
    desktop_targets = [
        os.path.join(user_home, "OneDrive", "Masaüstü"),
        os.path.join(user_home, "OneDrive", "Desktop"),
        os.path.join(user_home, "Desktop"),
        os.path.join(user_home, "Masaüstü")
    ]
    
    deployed_paths = []
    seen = set()
    # Terminate running process if any so files are not locked
    try:
        subprocess.run(["taskkill", "/F", "/IM", "localdictionary.exe"], capture_output=True)
        import time; time.sleep(0.5)
    except Exception:
        pass

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

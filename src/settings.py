import os
import json
from typing import Dict, Any, Optional
from src.utils import get_resource_path

SETTINGS_FILE = get_resource_path(os.path.join("data", "settings.json"))

DEFAULT_SETTINGS: Dict[str, Any] = {
    "theme": "dark",                              # "dark", "light", "system"
    "language": "tr",                             # "tr", "en"
    "always_on_top": False,                       # Keep window on top
    "ctrl_right_click_translate": True,           # Option 1: Ctrl + Right Click Quick Translate Popup
    "selection_translate": True,                  # Option 2: Show floating button on text selection anywhere
    "double_click_translate": False,              # Option 2b: Show floating button on double-click selection
    "right_click_translate": True,                # Option 3: Show floating button on right-click
    "windows_context_menu": True,                 # Windows Shell Context Menu & Right Click Button
    "run_on_startup": True,                       # Windows auto-start toggle
    "startup_mode": "minimized",                  # "normal" (foreground/open) or "minimized" (system tray / taskbar)
    "minimize_to_tray": True,                     # Minimize to tray instead of quitting or keep in tray
    "in_app_context_menu": True,                  # Right click context menu inside app entries/textboxes
    "save_history": True,                         # Store search queries in history.db
    "show_slang_profanity": True,                 # Show/filter slang, colloquial, and vulgar content
    "default_direction": "auto"                   # "auto", "en_tr", "tr_en"
}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "tr": {
        # Header & Window
        "app_title": "LOCALDICTIONARY",
        "app_subtitle": "v1.41 (Açık Kaynak / 100% Çevrimdışı - BETA)",
        "history_btn": "🕒 Geçmiş",
        "settings_btn": "⚙️ Ayarlar",
        
        # Tabs (Only 2 tabs on main window)
        "tab_dict": "Sözlük",
        "tab_sentence": "Cümle Çevirisi (BETA)",

        # Dictionary Tab
        "search_dir_lbl": "Arama Yönü:",
        "dir_auto": "Otomatik",
        "dir_en_tr": "EN ➔ TR",
        "dir_tr_en": "TR ➔ EN",
        "search_placeholder": "Kelime veya deyim yazın... (Örn: computer, başarı, geldi, went, göz yummak)",
        "search_btn": "Ara",
        "clear_btn": "✕",
        "recent_searches": "Son Aramalar:",
        "col_source": "Kaynak Kelime / İfade",
        "col_type": "Tür",
        "col_category": "Kategori",
        "col_target": "Çeviri / Karşılık",
        "dict_detail_title": "Sözlük Tanımı & Bilgi",
        "copy_translation_btn": "Çeviriyi Kopyala",
        "copied_status": "Kopyalandı: '{word}'",
        "no_results": "'{query}' kelimesi için doğrudan eşleşme bulunamadı.\n\nİpucu: Yazımı kontrol edebilir veya üstteki 'Cümle Çevirisi' sekmesini deneyebilirsiniz.",
        "did_you_mean": "Bunu mu demek istediniz:",
        "results_found": "{count} sonuç bulundu ({ms:.1f} ms) — Yön: {direction}",

        # Sentence Translation Tab
        "sent_dir_lbl": "Çeviri Yönü:",
        "sent_dir_auto": "Otomatik Algıla",
        "sent_dir_en_tr": "İngilizce ➔ Türkçe",
        "sent_dir_tr_en": "Türkçe ➔ İngilizce",
        "sent_input_lbl": "Çevrilecek Cümle / Metin:",
        "sent_did_you_mean": "Bunu mu demek istediniz:",
        "translate_action_btn": "⚡ Çevir",
        "sent_clear_btn": "✕ Temizle",
        "sent_copy_btn": "📋 Çeviriyi Kopyala",
        "sent_edit_btn": "✏️ Doğrusunu Öğret",
        "btn_glossary": "📖 Terim Sözlüğü",
        "conf_high": "🟢 Güven: %{score} (Yüksek)",
        "conf_med": "🟡 Güven: %{score} (Orta)",
        "conf_low": "⚠️ Düşük Güven: %{score} (Kontrol Edin)",
        "conf_user": "✓ %100 (Kullanıcı Düzeltmesi)",
        "glossary_title": "📖 Özel Terim Sözlüğü (Glossary)",
        "glossary_sub": "Çeviride zorunlu olarak kullanılmasını istediğiniz özel terimleri tanımlayın.",
        "glossary_src": "Kaynak Terim:",
        "glossary_tgt": "Hedef Karşılık:",
        "glossary_add": "+ Terim Ekle",
        "glossary_del": "🗑️ Seçileni Sil",
        "correction_title": "✏️ Çeviriyi Düzelt & Sisteme Öğret",
        "correction_desc": "Bu cümlenin doğru çevirisini giriniz. Sistem bundan sonra bu çeviriyi hafızasında tutacaktır.",
        "correction_saved": "✓ Doğru çeviri kaydedildi ve sisteme öğretildi!",
        "sent_loading_done": "✓ Çeviri Tamamlandı",
        "sent_status_ready": "Cümle çevirisi tamamlandı.",
        "breakdown_title": "Cümle Ögeleri & Kelime Analizi:",
        "col_orig": "Kelime / İfade",
        "col_role": "Cümledeki Görevi",
        "col_pos": "Dilbilgisi",
        "col_trans": "Seçilen Çeviri",
        "col_alts": "Alternatifler",

        # Settings Window
        "settings_window_title": "⚙️ LocalDictionary Ayarları",
        "settings_window_sub": "Görünüm, kısayollar, Windows entegrasyonu ve sistem tercihleri",
        
        # Section 1: Appearance
        "sec_appearance": "🎨 Görünüm ve Pencere",
        "theme_lbl": "Arayüz Teması:",
        "theme_dark": "🌙 Koyu (Dark)",
        "theme_light": "☀️ Açık (Light)",
        "theme_system": "💻 Sistem",
        "always_on_top_lbl": "Pencereyi Her Zaman Üstte Tut (Always on Top)",
        "always_on_top_desc": "Uygulama penceresi diğer pencerelerin üzerinde sabit kalır.",

        # Section 2: Language
        "sec_language": "🌐 Uygulama ve Arayüz Dili",
        "lang_lbl": "Arayüz Dili (Interface Language):",
        "lang_tr": "🇹🇷 Türkçe",
        "lang_en": "🇬🇧 English",

        # Section 3: Right Click Translation Options
        "sec_right_click_options": "⚡ Sağ Tık & Metin Seçimi Çevirisi",
        "selection_translate_lbl": "Metin Seçildiğinde (Sürükleme) Çeviri Butonu Göster",
        "selection_translate_desc": "Tarayıcıda veya herhangi bir uygulamada fareyle metin seçilip sürüklendiğinde imlecin yanında [⚡ Çevir] butonu belirir.",
        "double_click_translate_lbl": "Kelimeye Çift Tıklandığında Çeviri Butonu Göster",
        "double_click_translate_desc": "Herhangi bir uygulamada bir kelimeye çift tıklandığında (sol çift tık) imlecin yanında [⚡ Çevir] butonu belirir. Rahatsız ediyorsa buradan kapatabilirsiniz.",
        "rc_translate_lbl": "Sağ Tık ile Çeviri Butonu Göster",
        "rc_translate_desc": "Seçili metne sağ tıklandığında imlecin yanında [⚡ LocalDictionary ile Çevir] butonu belirir.",
        "ctrl_rc_lbl": "Ctrl + Sağ Tık Hızlı Çeviri (Baloncuk)",
        "ctrl_rc_desc": "Herhangi bir programda (tarayıcı, Word, PDF vb.) metin seçilip Ctrl + Sağ Tık yapıldığında doğrudan hızlı çeviri kartını açar.",
        "win_ctx_lbl": "Windows Gezgini Sağ Tık Menüsü",
        "win_ctx_desc": "Windows Gezgini'nde dosya, klasör ve masaüstü sağ tık menüsüne 'LocalDictionary ile Çevir' seçeneğini ekler.",
        "win_ctx_active_notice": "✓ Arka planda ve sistem tepsisinde açık tutuluyor. Program kapalı olsa bile sağ tık çevirisi hazırdır.",
        "rc_inapp_lbl": "Uygulama İçi Sağ Tık Menüsü",
        "rc_inapp_desc": "Sözlük içindeki tüm alanlarda sağ tık ile kopyalama ve arama menüsü gösterir.",

        # Section 4: Startup Options
        "sec_startup": "🚀 Windows Başlangıç Tercihleri",
        "startup_enable_lbl": "Windows Başlangıcında Otomatik Başlat",
        "startup_enable_desc": "Bilgisayar her açıldığında LocalDictionary arka planda otomatik olarak hazır başlar.",
        "startup_mode_lbl": "Açılış Durumu (Pencere Görünümü):",
        "startup_mode_normal": "🖥️ Normal Açık (Üstte/Önde)",
        "startup_mode_minimized": "📥 Altta Açık (Simge Durumunda / Tepside)",
        "startup_mode_desc": "Bilgisayar açıldığında uygulamanın ekranda açık mı yoksa görev çubuğunda/tepside hazır mı başlayacağını belirler.",

        # Section 5: Taskbar & System Tray
        "sec_tray": "📌 Görev Çubuğu ve Bildirim Alanı (Tray)",
        "tray_desc": "LocalDictionary açık olduğu sürece Windows görev çubuğunda ve sağ alttaki sistem tepsisinde açık olduğunu belirtir.",
        "tray_minimize_lbl": "Kapatıldığında / Simge Durumuna Alındığında Arka Planda Açık Tut",
        "tray_minimize_desc": "Pencere kapatılsa bile sistem tepsisinde açık kalır ve Ctrl+Sağ Tık çevirisini anında yapmaya devam eder.",
        "tray_open": "LocalDictionary'i Aç / Göster",
        "tray_settings": "⚙️ Ayarlar",
        "tray_exit": "Çıkış",
        "tray_tooltip": "LocalDictionary (100% Çevrimdışı - Açık)",

        # Section 6: History & Storage
        "sec_history": "🕒 Geçmiş & Veri Depolama",
        "hist_save_lbl": "Arama Geçmişini Kaydet",
        "hist_save_desc": "Aramaları yerel veritabanında kalıcı olarak saklar.",
        "hist_clear_btn": "🗑️ Geçmişi Temizle",
        "hist_cleared_msg": "Arama geçmişi başarıyla temizlendi.",
        "hist_clear_confirm_title": "Geçmişi Temizle",
        "hist_clear_confirm_msg": "Tüm arama geçmişiniz kalıcı olarak silinecek. Onaylıyor musunuz?",
        "col_time": "Tarih / Saat",
        "btn_delete": "Sil",
        "btn_save": "💾 Kaydet & Sisteme Öğret",
        "btn_close": "Tamam / Kapat",

        # Section 6b: Content & Slang Preferences
        "sec_content": "🛡️ İçerik & Sokak Dili Tercihleri",
        "slang_profanity_lbl": "Argo ve Kaba İfadeleri Dahil Et (Slang & Profanity)",
        "slang_profanity_desc": "Sözlük aramalarında ve cümle çevirisinde sokak dili, argo ve küfürlü ifadeleri gösterir. Kapatıldığında bu ifadeler sansürlenir / temizlenir.",

        # Section 7: About
        "sec_about": "ℹ️ Sistem ve Veritabanı Bilgisi",
        "about_ver": "Sürüm: LocalDictionary v1.41 (Açık Kaynak / Open Source - BETA)",
        "about_db": "Veritabanı: 2.26+ Milyon Kayıt (Bilingual, Wiktionary, FreeDict, TDK, Webster)",
        "about_mode": "Çalışma Modu: 100% Çevrimdışı (İnternetsiz ve Yerel)",
        "about_license": "Lisans: Açık Kaynak (MIT / Apache 2.0 / GPL Uyumlu - Tamamen Ücretsiz)",
        "about_status_active": "● Durum: Arka planda aktif ve dinliyor",

        # Status Bar
        "status_ready": "Hazır",
        "status_translating": "Çevriliyor...",
        "status_engine_badge": "● 2.2M+ Sözlük & Açık Kaynak Yerel AI (BETA - 100% Çevrimdışı)",

        # Context Menu
        "ctx_search_dict": "🔍 Seçileni Sözlükte Ara",
        "ctx_send_sentence": "⚡ Cümle Çevirisine Gönder",
        "ctx_copy": "📋 Kopyala",
        "ctx_paste": "📌 Yapıştır",
        "ctx_cut": "✂️ Kes"
    },
    "en": {
        # Header & Window
        "app_title": "LOCALDICTIONARY",
        "app_subtitle": "v1.41 (Open Source / 100% Offline - BETA)",
        "history_btn": "🕒 History",
        "settings_btn": "⚙️ Settings",

        # Tabs (Only 2 tabs on main window)
        "tab_dict": "Dictionary",
        "tab_sentence": "Sentence Translation (BETA)",

        # Dictionary Tab
        "search_dir_lbl": "Direction:",
        "dir_auto": "Auto",
        "dir_en_tr": "EN ➔ TR",
        "dir_tr_en": "TR ➔ EN",
        "search_placeholder": "Type a word or idiom... (e.g. computer, success, came, went, turn a blind eye)",
        "search_btn": "Search",
        "clear_btn": "✕",
        "recent_searches": "Recent Searches:",
        "col_source": "Source Word / Phrase",
        "col_type": "Type",
        "col_category": "Category",
        "col_target": "Translation / Target",
        "dict_detail_title": "Dictionary Definition & Notes",
        "copy_translation_btn": "Copy Translation",
        "copied_status": "Copied: '{word}'",
        "no_results": "No direct matches found for '{query}'.\n\nTip: Check spelling or try the 'Sentence Translation' tab above.",
        "did_you_mean": "Did you mean:",
        "results_found": "{count} results found ({ms:.1f} ms) — Dir: {direction}",

        # Sentence Translation Tab
        "sent_dir_lbl": "Translation Direction:",
        "sent_dir_auto": "Auto Detect",
        "sent_dir_en_tr": "English ➔ Turkish",
        "sent_dir_tr_en": "Turkish ➔ English",
        "sent_input_lbl": "Sentence / Text to Translate:",
        "sent_did_you_mean": "Did you mean:",
        "translate_action_btn": "⚡ Translate",
        "sent_clear_btn": "✕ Clear",
        "sent_copy_btn": "📋 Copy Translation",
        "sent_edit_btn": "✏️ Teach Correction",
        "btn_glossary": "📖 Glossary",
        "conf_high": "🟢 Confidence: {score}% (High)",
        "conf_med": "🟡 Confidence: {score}% (Medium)",
        "conf_low": "⚠️ Low Confidence: {score}% (Review Advised)",
        "conf_user": "✓ 100% (User Correction)",
        "glossary_title": "📖 Custom Glossary Management",
        "glossary_sub": "Define custom term pairs to be enforced during translation.",
        "glossary_src": "Source Term:",
        "glossary_tgt": "Target Translation:",
        "glossary_add": "+ Add Term",
        "glossary_del": "🗑️ Delete Selected",
        "correction_title": "✏️ Correct & Teach Translation",
        "correction_desc": "Enter the accurate translation for this text. The system will prioritize it in future queries.",
        "correction_saved": "✓ Correction saved and learned by system!",
        "sent_loading_done": "✓ Translation Completed",
        "sent_status_ready": "Sentence translation completed.",
        "breakdown_title": "Sentence Components & Word Analysis:",
        "col_orig": "Word / Phrase",
        "col_role": "Sentence Role",
        "col_pos": "Grammar / POS",
        "col_trans": "Selected Translation",
        "col_alts": "Alternatives",

        # Settings Window
        "settings_window_title": "⚙️ LocalDictionary Settings",
        "settings_window_sub": "Appearance, shortcuts, Windows integration and system preferences",

        # Section 1: Appearance
        "sec_appearance": "🎨 Appearance & Window",
        "theme_lbl": "Theme Mode:",
        "theme_dark": "🌙 Dark",
        "theme_light": "☀️ Light",
        "theme_system": "💻 System",
        "always_on_top_lbl": "Keep Window Always on Top",
        "always_on_top_desc": "Keeps application floating above other open windows.",

        # Section 2: Language
        "sec_language": "🌐 Language & Interface",
        "lang_lbl": "Interface Language:",
        "lang_tr": "🇹🇷 Türkçe",
        "lang_en": "🇬🇧 English",

        # Section 3: Right Click Translation Options
        "sec_right_click_options": "⚡ Right Click & Text Selection Translation",
        "selection_translate_lbl": "Show Translate Button on Text Selection (Drag)",
        "selection_translate_desc": "When text is selected by mouse dragging in any browser or app, a [⚡ Translate] button appears near the cursor.",
        "double_click_translate_lbl": "Show Translate Button on Double-Click (Left Double Click)",
        "double_click_translate_desc": "When double-clicking a word with left click in any application, shows a [⚡ Translate] button. Can be disabled if intrusive.",
        "rc_translate_lbl": "Show Translate Button on Right Click",
        "rc_translate_desc": "When right-clicking selected text in any app, a [⚡ Translate with LocalDictionary] button appears near the cursor.",
        "ctrl_rc_lbl": "Ctrl + Right Click Quick Translate (Floating Card)",
        "ctrl_rc_desc": "Displays an instant floating translation card next to the cursor when you select text and press Ctrl + Right Click in any application.",
        "win_ctx_lbl": "Windows Explorer Context Menu",
        "win_ctx_desc": "Adds 'Translate with LocalDictionary' to the Windows Explorer file, folder, and desktop right-click menu.",
        "win_ctx_active_notice": "✓ Kept active in background and system tray. Right-click translation is available even when window is closed.",
        "rc_inapp_lbl": "In-App Right-Click Context Menu",
        "rc_inapp_desc": "Shows context menu with search and copy inside the application fields.",

        # Section 4: Startup Options
        "sec_startup": "🚀 Windows Startup Preferences",
        "startup_enable_lbl": "Start Automatically on Windows Boot",
        "startup_enable_desc": "Automatically launches LocalDictionary in the background when Windows boots.",
        "startup_mode_lbl": "Startup Launch State:",
        "startup_mode_normal": "🖥️ Open Normally (Foreground)",
        "startup_mode_minimized": "📥 Start Minimized (System Tray / Taskbar)",
        "startup_mode_desc": "Controls whether the app window opens in front or starts minimized in the tray ready for shortcuts.",

        # Section 5: Taskbar & System Tray
        "sec_tray": "📌 Taskbar & System Tray",
        "tray_desc": "LocalDictionary displays in the Windows taskbar and system tray whenever active.",
        "tray_minimize_lbl": "Keep Active in Background when Closed/Minimized",
        "tray_minimize_desc": "Keeps the app running in the background for instant translations even if the window is closed.",
        "tray_open": "Open / Show LocalDictionary",
        "tray_settings": "⚙️ Settings",
        "tray_exit": "Exit",
        "tray_tooltip": "LocalDictionary (100% Offline - Active)",

        # Section 6: History & Storage
        "sec_history": "🕒 History & Data Storage",
        "hist_save_lbl": "Save Search History",
        "hist_save_desc": "Persists search queries locally in SQLite history database.",
        "hist_clear_btn": "🗑️ Clear History",
        "hist_cleared_msg": "Search history cleared successfully.",
        "hist_clear_confirm_title": "Clear History",
        "hist_clear_confirm_msg": "Are you sure you want to permanently clear your search history?",
        "col_time": "Date / Time",
        "btn_delete": "Delete",
        "btn_save": "💾 Save & Teach",
        "btn_close": "Close",

        # Section 6b: Content & Slang Preferences
        "sec_content": "🛡️ Content & Slang Preferences",
        "slang_profanity_lbl": "Include Slang & Profanity",
        "slang_profanity_desc": "Shows colloquial slang, street expressions, and profanity in dictionary and sentence translations. When disabled, these expressions are censored / filtered.",

        # Section 7: About
        "sec_about": "ℹ️ System & Database Information",
        "about_ver": "Version: LocalDictionary v1.41 (Open Source - BETA)",
        "about_db": "Database: 2.26+ Million Records (Bilingual, Wiktionary, FreeDict, TDK, Webster)",
        "about_mode": "Mode: 100% Offline (Local & Zero Setup)",
        "about_license": "License: Open Source (MIT / Apache 2.0 / GPL Compatible - 100% Free)",
        "about_status_active": "● Status: Local AI engine active and ready",

        # Status Bar
        "status_ready": "Ready",
        "status_translating": "Translating...",
        "status_engine_badge": "● 2.2M+ Dictionary & Open Source Local AI (BETA - 100% Offline)",

        # Context Menu
        "ctx_search_dict": "🔍 Search in Dictionary",
        "ctx_send_sentence": "⚡ Send to Sentence Translator",
        "ctx_copy": "📋 Copy",
        "ctx_paste": "📌 Paste",
        "ctx_cut": "✂️ Cut"
    }
}

class SettingsManager:
    """Manages persistent application settings in a JSON file."""
    def __init__(self, filepath: Optional[str] = None):
        self.filepath = filepath or SETTINGS_FILE
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath) and os.path.getsize(self.filepath) > 0:
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        # Migrate old key right_click_translate if present
                        if "right_click_translate" in saved and "ctrl_right_click_translate" not in saved:
                            saved["ctrl_right_click_translate"] = saved["right_click_translate"]
                        self.settings.update(saved)
            except Exception as e:
                print(f"Uyarı: Ayarlar dosyası okunamadı ({e}), varsayılanlar kullanılıyor.")
        return self.settings

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Hata: Ayarlar kaydedilemedi: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save()

    def get_text(self, key: str) -> str:
        lang = self.get("language", "tr")
        lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["tr"])
        return lang_dict.get(key, TRANSLATIONS["tr"].get(key, key))

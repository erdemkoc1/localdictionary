import os
import json
from typing import Dict, Any, Optional
from src.utils import get_resource_path

SETTINGS_FILE = get_resource_path(os.path.join("data", "settings.json"))

DEFAULT_SETTINGS: Dict[str, Any] = {
    "theme": "dark",                   # "dark", "light", "system"
    "language": "tr",                  # "tr", "en"
    "right_click_translate": True,     # Global right click / quick translate
    "right_click_trigger": "ctrl_right_click", # "ctrl_right_click", "clipboard"
    "in_app_context_menu": True,       # Right click menu inside the application
    "save_history": True,              # Store search queries in history.db
    "default_direction": "auto"        # "auto", "en_tr", "tr_en"
}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "tr": {
        # Header & Window
        "app_title": "LOCALDICTIONARY",
        "app_subtitle": "v1.4 (100% Çevrimdışı - Taşınabilir)",
        "history_btn": "🕒 Geçmiş",
        "settings_btn": "⚙️ Ayarlar",
        
        # Tabs
        "tab_dict": "🔍 Sözlük / Kelime Arama",
        "tab_sentence": "⚡ Cümle & Sentaks Çevirisi (BETA)",
        "tab_settings": "⚙️ Ayarlar",

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
        "no_results": "'{query}' kelimesi için doğrudan eşleşme bulunamadı.\n\nİpucu: Yazımı kontrol edebilir veya üstteki '⚡ Cümle & Sentaks Çevirisi' sekmesini deneyebilirsiniz.",
        "results_found": "{count} sonuç bulundu ({ms:.1f} ms) — Yön: {direction}",

        # Sentence Translation Tab
        "sent_dir_lbl": "Çeviri Yönü:",
        "sent_dir_auto": "Otomatik Algıla",
        "sent_dir_en_tr": "İngilizce ➔ Türkçe",
        "sent_dir_tr_en": "Türkçe ➔ İngilizce",
        "sent_input_lbl": "Çevrilecek Cümle / Metin:",
        "translate_action_btn": "⚡ Çevir (Sentaks & Sözlük Motoru)",
        "sent_clear_btn": "✕ Temizle",
        "sent_copy_btn": "📋 Çeviriyi Kopyala",
        "sent_loading_done": "✓ Çeviri Tamamlandı",
        "sent_status_ready": "Cümle & Sentaks çevirisi tamamlandı.",
        "breakdown_title": "Cümle Ögeleri & Sözlük Karşılıkları (Sentaks Analizi):",
        "col_orig": "Kelime / İfade",
        "col_role": "Sentaks Rolü",
        "col_pos": "Dilbilgisi",
        "col_trans": "Seçilen Çeviri",
        "col_alts": "Alternatifler",

        # Settings Tab
        "settings_header": "UYGULAMA AYARLARI",
        "settings_desc": "Görünüm, arayüz dili, sağ tık çevirisi ve sistem tercihlerinizi buradan yapılandırabilirsiniz.",
        
        # Section 1: Appearance
        "sec_appearance": "🎨 Görünüm ve Tema",
        "theme_lbl": "Arayüz Teması:",
        "theme_dark": "🌙 Koyu (Dark)",
        "theme_light": "☀️ Açık (Light)",
        "theme_system": "💻 Sistem",

        # Section 2: Language
        "sec_language": "🌐 Uygulama ve Arayüz Dili",
        "lang_lbl": "Arayüz Dili (Interface Language):",
        "lang_tr": "🇹🇷 Türkçe",
        "lang_en": "🇬🇧 English",

        # Section 3: Right Click Translate
        "sec_right_click": "⚡ Sağ Tık & Hızlı Çeviri (Pop-up)",
        "rc_enable_lbl": "Hızlı Çeviri Baloncuğunu Etkinleştir",
        "rc_enable_desc": "Herhangi bir Windows uygulamasında metin seçilip tetiklendiğinde imlecin yanında anlık çeviri kutusu gösterir.",
        "rc_trigger_lbl": "Çeviri Tetikleme Yöntemi:",
        "trigger_ctrl_rc": "Ctrl + Sağ Tık (Önerilen)",
        "trigger_clipboard": "Pano Kopyalama (Ctrl+C)",
        "rc_inapp_lbl": "Uygulama İçi Sağ Tık Menüsü",
        "rc_inapp_desc": "Sözlük içindeki tüm alanlarda sağ tık ile arama ve kopyalama menüsü gösterir.",

        # Section 4: History & Storage
        "sec_history": "🕒 Geçmiş & Veri Depolama",
        "hist_save_lbl": "Arama Geçmişini Kaydet",
        "hist_save_desc": "Aramaları yerel veritabanında kalıcı olarak saklar.",
        "hist_clear_btn": "🗑️ Geçmişi Temizle",
        "hist_cleared_msg": "Arama geçmişi başarıyla temizlendi.",

        # Section 5: About
        "sec_about": "ℹ️ Hakkında ve Sistem Bilgisi",
        "about_ver": "Sürüm: LocalDictionary v1.4 Taşınabilir",
        "about_db": "Veritabanı: 2.26+ Milyon Kayıt (Bilingual, Wiktionary, FreeDict, TDK, Webster)",
        "about_mode": "Çalışma Modu: 100% Çevrimdışı (İnternetsiz ve Yerel)",
        "about_license": "Lisans: Açık Kaynak ve Ücretsiz",

        # Status Bar
        "status_ready": "Hazır",
        "status_engine_badge": "● 2.2M+ Sözlük & Sentaks Motoru (100% Çevrimdışı)",

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
        "app_subtitle": "v1.4 (100% Offline - Portable)",
        "history_btn": "🕒 History",
        "settings_btn": "⚙️ Settings",

        # Tabs
        "tab_dict": "🔍 Dictionary / Word Search",
        "tab_sentence": "⚡ Sentence & Syntax Translation (BETA)",
        "tab_settings": "⚙️ Settings",

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
        "no_results": "No direct matches found for '{query}'.\n\nTip: Check spelling or try the '⚡ Sentence & Syntax Translation' tab above.",
        "results_found": "{count} results found ({ms:.1f} ms) — Dir: {direction}",

        # Sentence Translation Tab
        "sent_dir_lbl": "Translation Direction:",
        "sent_dir_auto": "Auto Detect",
        "sent_dir_en_tr": "English ➔ Turkish",
        "sent_dir_tr_en": "Turkish ➔ English",
        "sent_input_lbl": "Sentence / Text to Translate:",
        "translate_action_btn": "⚡ Translate (Syntax & Dictionary Engine)",
        "sent_clear_btn": "✕ Clear",
        "sent_copy_btn": "📋 Copy Translation",
        "sent_loading_done": "✓ Translation Completed",
        "sent_status_ready": "Sentence & Syntax translation completed.",
        "breakdown_title": "Sentence Elements & Dictionary Matches (Syntax Analysis):",
        "col_orig": "Word / Phrase",
        "col_role": "Syntax Role",
        "col_pos": "Grammar (POS)",
        "col_trans": "Selected Translation",
        "col_alts": "Alternatives",

        # Settings Tab
        "settings_header": "APPLICATION SETTINGS",
        "settings_desc": "Configure appearance, interface language, right-click translate, and system preferences.",

        # Section 1: Appearance
        "sec_appearance": "🎨 Appearance & Theme",
        "theme_lbl": "Theme Mode:",
        "theme_dark": "🌙 Dark",
        "theme_light": "☀️ Light",
        "theme_system": "💻 System",

        # Section 2: Language
        "sec_language": "🌐 Language & Interface",
        "lang_lbl": "Interface Language:",
        "lang_tr": "🇹🇷 Türkçe",
        "lang_en": "🇬🇧 English",

        # Section 3: Right Click Translate
        "sec_right_click": "⚡ Right-Click & Quick Translation (Pop-up)",
        "rc_enable_lbl": "Enable Quick Translation Popup",
        "rc_enable_desc": "Displays an instant floating translation box when selecting text in any Windows application.",
        "rc_trigger_lbl": "Trigger Method:",
        "trigger_ctrl_rc": "Ctrl + Right Click (Recommended)",
        "trigger_clipboard": "Clipboard Copy (Ctrl+C)",
        "rc_inapp_lbl": "In-App Right-Click Context Menu",
        "rc_inapp_desc": "Shows context menu with search and copy inside the application fields.",

        # Section 4: History & Storage
        "sec_history": "🕒 History & Data Storage",
        "hist_save_lbl": "Save Search History",
        "hist_save_desc": "Persists search queries locally in SQLite history database.",
        "hist_clear_btn": "🗑️ Clear History",
        "hist_cleared_msg": "Search history cleared successfully.",

        # Section 5: About
        "sec_about": "ℹ️ About & System Information",
        "about_ver": "Version: LocalDictionary v1.4 Portable",
        "about_db": "Database: 2.26+ Million Records (Bilingual, Wiktionary, FreeDict, TDK, Webster)",
        "about_mode": "Mode: 100% Offline (Local & Zero Setup)",
        "about_license": "License: Open Source & Free",

        # Status Bar
        "status_ready": "Ready",
        "status_engine_badge": "● 2.2M+ Dictionary & Syntax Engine (100% Offline)",

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

# LocalDictionary (TR ⇄ EN) v1.41 (BETA)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-0078D6.svg)](https://www.microsoft.com/windows)
[![Offline: 100%](https://img.shields.io/badge/Privacy-100%25%20Offline-green.svg)](#gizlilik-ve-guvenlik)

**LocalDictionary**, Türkçe ve İngilizce dilleri arasında çift yönlü çalışan, **%100 çevrimdışı, açık kaynaklı, gizlilik odaklı hibrit sözlük ve nöral cümle çevirisi masaüstü uygulamasıdır**.

Hiçbir bulut servisine, harici API'ye veya internet bağlantısına ihtiyaç duymaz. Tüm sözlük aramaları ve yapay zeka çevirileri tamamen yerel donanımınızda (CPU) çalışır.

---

## 🌟 Temel Özellikler

### 1. 2.2M+ Kayıtlı Derin Sözlük & Çok Anlamlılık (Polysemy)
* **1.68M+ Çift Yönlü Kayıt:** 263.000+ tekil İngilizce kök ve 888.000+ tekil Türkçe kök kelime.
* **CEFR A1–C2 Seviye Etiketleme:** 260.000'den fazla kayıt CEFR (A1, A2, B1, B2, C1, C2) ve Academic Word List (AWL) seviyelerine göre etiketlenmiştir.
* **Akıllı Sıralama (Re-Ranking):** Kelimelerin onlarca anlamı arasından birincil ve en yaygın olanları daima ilk sıralarda sunulur.
* **TDK & Webster Monolingual Sözlükler:** 133.000+ TDK Güncel Türkçe Sözlük tanımı ve 102.000+ Webster İngilizce tanımı dahildir.
* **Alt-milisaniye Arama Hızı:** SQLite WAL (Write-Ahead Logging) indeksi ile anlık (~0.8 ms) arama performansı.

### 2. Hibrit Çeviri Motoru (Yerel AI + Kural Tabanlı Sistem)
* **CTranslate2 NMT:** Argos Translate / Opus-MT modelleri INT8 kuantizasyonu ile yerel CPU üzerinde hızlı çalışır.
* **Deyimler ve Atasözleri Motoru:** Binlerce Türkçe ve İngilizce kalıplaşmış deyimi ve atasözünü birebir çeviri hatasına düşmeden doğal karşılıklarıyla aktarır.
* **Cümle Ayrıştırma (Clause Splitting):** Uzun ve karmaşık bileşik cümleleri mantıksal yan tümcelere bölerek çeviri başarısını artırır.
* **Dinamik Güven Skoru:** Her çeviride yeşil (%80+ yüksek), sarı (%55-79 orta) ve kırmızı (düşük güven uyarısı) göstergeleri sunar.

### 3. İnsan Odaklı Öğrenme ve Özel Sözlük (Human-in-the-Loop)
* **"Doğrusunu Öğret":** Beğenilmeyen veya geliştirilmek istenen bir çevirinin doğrusu tek tuşla sisteme öğretilir; sistem sonraki sorgularda bu öğrenilen çeviriyi anında önceliklendirir.
* **Özel Terim Sözlüğü (Glossary):** Çevirilerde zorunlu olarak kullanılmasını istediğiniz terim eşleştirmelerini tanımlayabilirsiniz.

### 4. Windows Entegrasyonu ve Hızlı Çeviri
* **Ctrl + Sağ Tık Hızlı Çeviri:** Herhangi bir programda (tarayıcı, PDF, Word vb.) seçili metin üzerinde `Ctrl + Sağ Tık` yapıldığında anında çeviri kartı açılır.
* **Sistem Tepsisi (System Tray):** Pencere simge durumuna alındığında arka planda sessizce hazır bekler.
* **Açık / Koyu Tema & Dil Desteği:** Türkçe ve İngilizce arayüz, koyu (Dark) ve açık (Light) tema seçenekleri.

---

## 🔒 Gizlilik ve Güvenlik (Privacy-First)

* **Sıfır Bulut Bağımlılığı:** API anahtarı, sunucu hesabı veya harici bağlantı kesinlikle bulunmaz.
* **Sıfır Telemetri:** Hiçbir veri, metin veya kullanım istatistiği dışarıya aktarılmaz; tüm veritabanları yerel diskinizde saklanır.
* **Açık Kaynak Kod:** Tüm kodlar incelenebilir, değiştirilebilir ve yerel olarak derlenebilir.

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
* Python 3.10 veya üzeri
* Windows 10 / 11 (64-bit)

### Kaynak Koddan Çalıştırma
```bash
# Depoyu klonlayın
git clone https://github.com/kullanici-adi/localdictionary.git
cd localdictionary

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
python main.py
```

### Taşınabilir Windows (.exe) Derleme
Kurulum gerektirmeyen tek parça taşınabilir Windows klasörü oluşturmak için:
```bash
python build_exe.py
```
Derleme tamamlandığında `dist/localdictionary/localdictionary.exe` dosyası hazır hale gelir.

---

## 🧪 Testleri Çalıştırma

Tüm birim ve entegrasyon testlerini çalıştırmak için:
```bash
python -m unittest tests/test_translator.py tests/test_syntax.py tests/test_db.py
```

---

## 📄 Lisans ve Kaynaklar

Bu proje [MIT Lisansı](LICENSE) altında dağıtılmaktadır.

* **Çeviri Modelleri:** [Argos Translate](https://github.com/argosopentech/argos-translate) / [Opus-MT](https://github.com/Helsinki-NLP/Opus-MT) (MIT & CC-BY-4.0)
* **Sözlük Verileri:** Kaikki Wiktionary (CC-BY-SA 3.0), FreeDict (GPL), Academic Word List (AWL), TDK & Webster kamuya açık kaynakları.

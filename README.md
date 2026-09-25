# LocalDictionary (TR ⇄ EN) v1.42.0-beta.1

**LocalDictionary**, Türkçe ve İngilizce arasında çalışan, gizlilik odaklı,
tamamen yerel bir masaüstü sözlük ve nöral çeviri uygulamasıdır.

> **BETA:** Bu sürüm geliştirme ve geri bildirim içindir. Kurulum gerektirmeyen
> Windows paketi GitHub Releases üzerinden dağıtılacaktır.

## Özellikler

- Indexed SQLite bilingual sözlük ve morfolojik arama
- Yerel CTranslate2 + SentencePiece nöral çeviri
- Kural tabanlı sözdizimi fallback'i
- Deyim/atasözü eşleştirme
- Yazım önerileri
- Kullanıcı düzeltmeleri, glossary ve çeviri önbelleği
- Türkçe/İngilizce arayüz
- Windows tray, Ctrl+sağ tık ve seçim çevirisi (kullanıcı açıkça etkinleştirirse)

## Gizlilik ve ağ davranışı

- Runtime'da bulut API, telemetri, güncelleme istemcisi veya uzak paket
  indeksi yoktur.
- NMT modelleri EXE'nin yanındaki `data/models` klasöründen yerel olarak
  okunur.
- Uygulama açılış veya çeviri sırasında internet bağlantısı açmaz; runtime
  ayrıca Python seviyesinde socket/ DNS bağlantılarını process içinde bloke
  eder.
- Geliştirici veri indirme scriptleri ağ kullanabilir; bunlar uygulama
  runtime'ının parçası değildir ve release paketine dahil edilmez.
- Ayarlar, geçmiş, öğrenilen düzeltmeler, glossary ve cache varsayılan olarak
  `%LOCALAPPDATA%\LocalDictionary` altında saklanır. OneDrive'a taşınabilir
  klasörde çalıştırılsanız bile bu dosyalar EXE yanında oluşturulmaz.

## İlk kullanım ve tercihler

- İlk açılış dili **İngilizce**dir.
- Kullanıcı Türkçe'yi seçtiğinde seçim kalıcı olarak saklanır ve sonraki
  açılışlarda korunur.
- Global quick translate özellikleri, Windows context menu ve otomatik
  başlangıç ilk kullanımda **kapalıdır**.
- Kullanıcı bir özelliği açtığında ayar `settings.json` içinde kalıcı olur ve
  uygulama yeniden açıldığında aynı tercih geri yüklenir.
- Uygulama veritabanı ve modelleri salt okunur kaynaklardır; kullanıcı
  değişiklikleri bu kaynakların üzerine yazılmaz.

## Kaynak koddan çalıştırma

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

İlk kaynak klonunda küçük bir starter dictionary oluşturulur. Tam veritabanı
ve NMT modelleri release paketinde bulunur; modeller yoksa uygulama kural
tabanlı fallback ile çalışmaya devam eder.

## Testler

```powershell
python -B -m unittest discover -s tests -v
```

Testler geçici veri dizinlerini kullanır; gerçek Windows Registry'yi,
kullanıcı geçmişini veya settings dosyasını değiştirmez.

## Windows paketi

```powershell
python -m pip install -r requirements-dev.txt
python build_exe.py
```

Çıktı:

- `dist/localdictionary/`
- `dist/LocalDictionary-v1.42.0-beta.1-win64.zip`
- `SHA256SUMS.txt`
- `RELEASE_MANIFEST.json`

Build scripti Desktop'a otomatik kopyalamaz, çalışan uygulamayı zorla
kapatmaz ve kullanıcı verilerini paketlemez. EXE imzasızdır; yayınlamadan
önce `SHA256SUMS.txt` değerlerini doğrulayın.

## Lisans ve kaynaklar

Kod: MIT (bkz. `LICENSE`).

Sözlük verileri ve modeller ayrı lisanslara tabidir; tamamen MIT kapsamında
değildir. `DATA_LICENSES.md`, `THIRD_PARTY_NOTICES.md` ve `LICENSES/` dizini release
paketine dahil edilir. TDK veya yeniden dağıtım izni belgelenmeyen sözlük
verisi public release veritabanına dahil edilmez.

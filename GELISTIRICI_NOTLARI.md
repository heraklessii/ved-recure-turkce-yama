# Ved: Recure Türkçe Yama — Geliştirici Notları

## Klasörler
- `tr/` — Çeviriler. `bNNN.json` (anahtar → Türkçe), `b-auto.json` (kalıp satırlardan otomatik üretilir, elle düzenleme),
  `arketip.json` (Buff/arketip adları sözlüğü), `SOZLUK.md` (terim sözlüğü).
- `src/` — İngilizce kaynak metinlerin 43 partiye bölünmüş hâli, `all.json` tamamı.
- `build/` — `en_original.csv` (oyundan çıkarılan orijinal İngilizce CSV), `tr.csv` (üretilen Türkçe), `fonts_plan.pkl`.
- `patch/` — `objects.pkl` + `ress.pkl` (oyuna yazılacak ham veriler).
- `../paket/VedRecure_TurkceYama/` — Dağıtılan paket (`Yamayi_Kur.bat`, `Yamayi_Kaldir.bat`, `veri/yama.ps1`, `veri/turkce.yama`).

## Çeviri düzeltme akışı
Python ortamı: `uv venv -p 3.12 .venv && uv pip install -p .venv UnityPy numpy scipy pillow freetype-py fonttools`
1. `tr/bNNN.json` içinde ilgili anahtarı düzelt (diyalog satırlarının sonundaki `$Komut[...]` kuyruğu otomatik eklenir, yazma).
2. `python assemble.py` → `build/tr.csv` üretir; `{0}`, `<color>`, `$n`, `%` gibi etiketleri doğrular (hata 0 olmalı).
3. Oyunu ORİJİNAL hâle getir (paketteki `Yamayi_Kaldir.bat`). Aşağıdaki betikler yamalı oyunda çalışmayı reddeder.
   - Font değiştiyse: `python build_fonts.py` → `build/fonts_plan.pkl`
   - Sabit (CSV dışı) metinler değiştiyse: `sabit_metin.py` içindeki `DEGISIKLIKLER` listesini düzenle, `python sabit_metin.py` → `build/sabit_metin.pkl`
4. `python make_patch.py` → `patch/*.pkl` (CSV + fontlar + sabit metinler).
5. `python pack.py` → `paket/.../veri/turkce.yama`.
6. Paketi test et: Kur → oyunda kontrol → Kaldır. Sürüm numarasını BENIOKU.txt'de artır, zip'le.

## Sabit metinler (v1.1)
- "NOW LOADING" → "HAZIRLANIYOR" (10 nesne; font Bahnschrift SDF_outlineGrery'de Ü/İ'ye yer yok, bu yüzden ASCII harfli kelime)
- Ana menü "Languages" → "Dil"; dil seçicilerde "English" → "Türkçe" (SelectorUI seçenekleri sıra ile çalışır, yalnızca görünen ad)

## Teknik özet
- Oyun: Unity 2022.3.7f1, IL2CPP, özel CSV yerelleştirme (`localization/english/translation`, resources.assets pathID 13066, UTF-8 BOM + CRLF).
- Dil: "English" dosyası Türkçe ile değiştirilir (yeni dil eklemek IL2CPP kod değişikliği gerektirir).
- Fontlar statik TMP SDF atlasları. Türkçe glifler: TTF'si olanlarda (Barlow, Bahnschrift, Anton, Archivo) FreeType ile, olmayanlarda
  (VedEnglish, VedAllLanguage — Source Han Sans) atlastaki gliflerden kompozisyonla üretilir. SDF spread = 1/(2·(padding+1)).
  Yer yoksa glif düşük çözünürlükte konur ve `glyph.scale = 1/f` ile büyütülür. Yerleşemeyen fontlar atlanır (4 adet 1024px Bahnschrift kontur).
- Yazma yöntemi: değişen nesneler `.assets` sonuna eklenir, nesne tablosu kaydı ve başlıktaki dosya boyutu güncellenir;
  atlas pikselleri `.resS` içine yerinde yazılır. Kurulum öncesi değişen her baytın orijinali `TurkceYama_yedek/yedek.bin`'e alınır.

## Kurulum programı (v1.2+)
- Kaynak: `kurulum/VedTurkceYama.cs` (.NET Framework 4, C# 5; Windows'ta yerleşik csc ile derlenir). `pack.py` çıktısı `kurulum/turkce.yama`'ya yazılır, `kurulum/derle.bat` exe'yi üretir (veri exe'ye gömülür).
- Orijinallik denetimi: appmanifest_3255500.acf + depot 3255501, steam_api64.dll / GameAssembly.dll / ved.exe SHA-256, emülatör dosya listesi. Oyun güncellenince SHA-256 değerlerini `Sabit.OrijinalDosyalar`'da güncelle.
- `test_motor.cs`: konsol test aracı (`kur`, `kaldir`, `sahte`, `ekran <png>`). Derleme: `/main:VedTurkceYama.TestMain` ile iki dosya birlikte.
- DİKKAT: pack.py nesne tablosu kaydını pathID+byteStart+byteSize üçlüsüyle arar (yalnızca pathID ile arama yanlış kayda denk gelebiliyordu — v1.2'de düzeltildi).
- Yapımcı: heraklessi (Discord: heraklessi) — `Sabit.Yapimci/Discord`.

## v1.3
- **Font ölçeği hatası:** Atlasa sığmayan Türkçe harfler düşük çözünürlükte konuyor, eskiden `glyph.scale = 1/f` ile büyütülüyordu.
  TMP satırın yükseklik ve ascender değerlerini glyph.scale ile çarptığı için Türkçe harf içeren satırlar aşağı kayıyordu
  (ÖZELLİK başlığı SALDIRI satırının üstüne biniyordu). Artık `glyph.scale = 1`; metrikler tam boyda veriliyor, glif kutusu
  SDF yayılımı ((pad+1)·f düşük çözünürlük pikseli) kadar genişletiliyor (`fontgen.render`).
- **Resimli yazılar:** `gorsel/` — `en/` orijinal PNG'ler (+ diğer dil sürümleri), `tr/` çıktılar.
  `dugmeler.py` (btn_*), `buff.py` (buffTitle_*; yazı maskesi 4 dil sürümünün farkından, noktalı panel 11 px periyotla onarılır),
  `basliklar.py` (TOPLAM HASAR, RASTGELE, EKİPMAN DEPOLANDI, DAVETİYE, LanguageTest→Dil), `duz.py` (sahte mağaza/kütüphane),
  `telefon.py` (phoneVX sohbeti). `paketle.py` → `build/gorseller.pkl` (resS içinde yerinde yazım; RGBA32/RGB24 birebir,
  DXT1/DXT5 etcpak ile). `python gorsel/paketle.py --denetle` orijinalleri yeniden kodlayıp doğrular.
- **Dil seçicideki "English":** IL2CPP metin sabiti. `metadata_yama.py` sabit tablosunda "English" girdisini "English (Zimbabwe)"
  verisinin yerine yazılan "Türkçe"ye yönlendirir (dosya boyutu değişmez) → `build/metadata.pkl`.
- Ana menü "Languages" metni resources.assets'te 3 kopya daha (1853330/1893238/1930339; pasif nesne), görünen başlık ise
  sharedassets0 "LanguageTest" dokusudur.
- `make_patch.py` artık gorseller.pkl + metadata.pkl'yi de ekler ve bölgelerin çakışmadığını denetler.
- Derleme: `derle.bat` bazen cmd'den bulunamıyor; csc komutunu doğrudan çalıştırın.

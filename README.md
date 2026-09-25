# Ved: Recure — Türkçe Yama

[Ved: Recure](https://store.steampowered.com/app/3255500/) için gayriresmî, ücretsiz Türkçe yama.
Hazırlayan: **heraklessi** (Discord: `heraklessi`)

**[⬇ Son sürümü indir](../../releases/latest)**

## Kapsam

- Menüler, ayarlar ve sistem mesajları
- Tüm hikâye ve diyaloglar (5 bölüm + final), ara sahne altyazıları, karakter sohbetleri
- Karakter yetenekleri, Buff'lar, ekipmanlar, eşya ve canavar açıklamaları
- Eğitimler, yükleme ekranı ipuçları, jenerik
- Resimli düğme ve başlıklar (Satın Al, Güçlendir, Buff başlıkları, TOPLAM HASAR, DAVETİYE, telefon sohbeti…)
- Oyunun kendi yazı tiplerine eklenen Türkçe karakterler: `ç ğ ı ö ş ü Ç Ğ İ Ö Ş Ü â î û`

Yaklaşık 4.600 satır. Tutarlı terimler için bkz. [`tr/SOZLUK.md`](tr/SOZLUK.md).

## Kurulum

1. Oyunu kapatın.
2. [Releases](../../releases/latest) sayfasından zip'i indirip açın, `VedTurkceYama.exe`'yi çalıştırın.
3. Denetimler yeşilse **YAMAYI KUR**'a basın.
   Kurulum için **internet bağlantısı gerekir**: program bu sayfadaki son sürümü denetler; elinizdeki sürüm eskiyse kurulum yapılmaz.
4. Oyunda **Ayarlar > Dil** bölümünden **Türkçe**'yi seçin (yama İngilizcenin yerine geçer).

**Kaldırmak için:** Aynı programda **Yamayı Kaldır**'a basın. Kurulumda alınan yedekten orijinal dosyalar birebir geri yüklenir.

### Notlar

- Yama yalnızca Steam'den edinilmiş orijinal kopyaya kurulur. Program, oyun sürümü uyuşmazsa hiçbir dosyaya dokunmadan durur.
- Uyumlu oyun sürümü: **0.0.1872 (Steam build 25535904)**.
- Steam'de "Oyun dosyalarının bütünlüğünü doğrula" yamayı siler; yeniden kurmanız yeterlidir.
- Oyun güncellendikten sonra **Yamayı Kaldır** yalnızca hâlâ yamalı olan dosyaları geri alır, güncellemeyle değişen dosyalara dokunmaz
  (internet gerektirmez). Ardından Steam'de dosya bütünlüğünü doğrulamanız önerilir.
- Kayıt dosyalarınıza dokunulmaz.
- Program imzasız olduğu için Windows SmartScreen uyarı verebilir ("Ek bilgi" > "Yine de çalıştır").
  Birkaç antivirüsün yapay zekâ tabanlı (ML) tespiti de imzasız, yeni programlar için yanlış alarm verebilir.
  Kaynak kodun tamamı bu depodadır.

### Bilinen eksikler

- Oyun modlarının tanıtım ekran görüntüleri, oyun içi sahte mağaza sayfası gibi büyük ve çok yazılı resimler ile logo altındaki slogan İngilizce kalmıştır.

## Kaynaktan derleme

Bu depoda oyunun orijinal metinleri, görselleri ve yazı tipleri **bulunmaz**; bunlar kendi oyun kopyanızdan çıkarılır.
Ayrıntılı iş akışı: [`GELISTIRICI_NOTLARI.md`](GELISTIRICI_NOTLARI.md).

```bash
pip install -r requirements.txt
python cikar.py        # oyun ORİJİNAL hâldeyken: build/en_original.csv
python split.py        # src/ (çeviri partileri için İngilizce kaynak)
python assemble.py     # tr/*.json -> build/tr.csv
python build_fonts.py  # Türkçe glifler -> build/fonts_plan.pkl
python sabit_metin.py  # sahne içi sabit metinler
python gorsel/cikar_gorseller.py   # orijinal dokular -> gorsel/en/
# gorsel/ klasöründe: dugmeler.py, buff.py, basliklar.py, duz.py, telefon.py -> gorsel/tr/
python gorsel/paketle.py   # Türkçe görseller -> build/gorseller.pkl
python metadata_yama.py    # dil seçicideki ad
python make_patch.py
python pack.py "<oyun klasörü>" kurulum/turkce.yama
```

Kurulum programı Windows'ta yerleşik .NET Framework derleyicisiyle derlenir (`kurulum/derle.bat`).
`kurulum/banner.png` oyunun kendi görsellerinden üretildiği için depoda yoktur; 1240×340 boyutunda herhangi bir PNG kullanabilirsiniz.

## Nasıl çalışır?

- **Metin:** Oyunun İngilizce CSV'si (resources.assets, TextAsset) Türkçesiyle değiştirilir.
- **Yazı tipleri:** TextMeshPro SDF atlaslarına Türkçe glifler eklenir. TTF'si olan fontlarda FreeType ile üretilir, olmayanlarda mevcut gliflerden birleştirilir (ör. `İ` = `I` + `i`'nin noktası).
- **Görseller:** Dokular `.resS` dosyalarında yerinde değiştirilir (RGBA32/RGB24 birebir, DXT1/DXT5 yeniden sıkıştırılır).
- **Yazma yöntemi:** Değişen nesneler `.assets` dosyasının sonuna eklenir ve nesne tablosu güncellenir. Değişen her baytın orijinali `TurkceYama_yedek/` klasörüne yedeklenir.

## Katkı ve geri bildirim

Çeviri hatası, taşan metin veya bozuk görünüm için ekran görüntüsüyle [Issue](../../issues) açabilir ya da Discord'dan (`heraklessi`) ulaşabilirsiniz.

## Yasal

Bu yama gayriresmî bir hayran çalışmasıdır; oyunun geliştiricisi veya yayıncısıyla bağlantısı yoktur.
Oyun ve orijinal içeriği sahiplerine aittir. Oyunu desteklemek için Steam'den satın alın.
Araçların ve kurulum programının kaynak kodu [MIT lisansı](LICENSE) ile sunulur.

---

## English

Unofficial Turkish translation patch for **Ved: Recure** (Steam). Download the installer from [Releases](../../releases/latest),
run `VedTurkceYama.exe`, click **YAMAYI KUR** (install), then pick **Türkçe** in the game's language settings (it replaces English).
The installer checks this repository for the latest release (an internet connection is required to install; outdated installers refuse to
install), backs up every changed byte and can fully uninstall. Only the original Steam copy (build 25535904) is supported.
This repository contains the translation texts and the tooling (Python + C#); no game assets are included.

// Ved: Recure Türkçe Yama — kurulum programı (.NET Framework 4, C# 5)
// Derleme: derle.bat
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows.Forms;
using Microsoft.Win32;

[assembly: AssemblyTitle("Ved: Recure Türkçe Yama")]
[assembly: AssemblyProduct("Ved: Recure Türkçe Yama")]
[assembly: AssemblyDescription("Ved: Recure için gayriresmî Türkçe yama kurulum programı")]
[assembly: AssemblyCompany("heraklessi")]
[assembly: AssemblyCopyright("© 2026 heraklessi — Discord: heraklessi")]
[assembly: AssemblyVersion("1.3.0.0")]
[assembly: AssemblyFileVersion("1.3.0.0")]

namespace VedTurkceYama
{
    static class Sabit
    {
        public const string Surum = "1.3";
        public const string Yapimci = "heraklessi";
        public const string Discord = "heraklessi";
        public const string AppId = "3255500";
        public const string DepotId = "3255501";
        public const string BackupDir = "TurkceYama_yedek";
        public const string BackupFile = "yedek.bin";
        // Steam'den indirilen orijinal dosyaların SHA-256 özetleri (build 25483973)
        public static readonly string[][] OrijinalDosyalar = new string[][] {
            new string[] { "ved_Data\\Plugins\\x86_64\\steam_api64.dll", "1ADD7F151FA644870A735AE86E68D1F019F296130D8E7C0A7ED3ECC7482DCCBC" },
            new string[] { "GameAssembly.dll", "3AA828D6C41F1D09AB396435BA0F9F84AA922ADBA2C3B13E72F3654ED797FBD0" },
            new string[] { "ved.exe", "979E784B287E8DB65EADCED7D7E6B209EF1CEB7EB45AA329409C3101DFDD9915" },
        };
        // Steam emülatörü / kırık sürüm kalıntıları
        public static readonly string[] YasakliDosyalar = new string[] {
            "steam_appid.txt", "steam_emu.ini", "SmartSteamEmu.ini", "OnlineFix.ini", "OnlineFix64.dll", "ColdClientLoader.ini",
            "cream_api.ini", "CODEX.ini", "steam_api64_o.dll", "steam_interfaces.txt", "local_save.txt", "steamclient_loader_x64.exe",
            "ALI213.ini", "3DMGAME.ini", "valve.ini", "SteamConfig.ini", "unsteam.ini"
        };
        public static readonly string[] YasakliKlasorler = new string[] { "steam_settings", "SmartSteamEmu", "Goldberg", "steam_emu" };
    }

    // ---------------------------------------------------------------- yama motoru
    class Obj { public long Off; public byte[] Orig20; public byte[] Data; }
    class AssetPatch { public string Name; public long OrigSize; public byte[] OrigHeader; public List<Obj> Objs = new List<Obj>(); }
    class Region { public long Off; public byte[] Data; }
    class RessPatch { public string Name; public long Size; public List<Region> Regions = new List<Region>(); }

    class YamaVerisi
    {
        public List<AssetPatch> Assets = new List<AssetPatch>();
        public List<RessPatch> Ress = new List<RessPatch>();

        static string ReadStr(BinaryReader r) { int n = r.ReadUInt16(); return Encoding.UTF8.GetString(r.ReadBytes(n)); }

        public static YamaVerisi Yukle()
        {
            Stream s = Assembly.GetExecutingAssembly().GetManifestResourceStream("turkce.yama");
            if (s == null) throw new Exception("Yama verisi programın içinde bulunamadı.");
            var v = new YamaVerisi();
            using (var r = new BinaryReader(s))
            {
                if (Encoding.ASCII.GetString(r.ReadBytes(5)) != "VEDTR" || r.ReadByte() != 1) throw new Exception("Yama verisi bozuk.");
                uint na = r.ReadUInt32();
                for (uint i = 0; i < na; i++)
                {
                    var a = new AssetPatch(); a.Name = ReadStr(r); a.OrigSize = (long)r.ReadUInt64(); a.OrigHeader = r.ReadBytes(48);
                    uint no = r.ReadUInt32();
                    for (uint j = 0; j < no; j++)
                    {
                        var o = new Obj(); o.Off = (long)r.ReadUInt64(); o.Orig20 = r.ReadBytes(20); o.Data = r.ReadBytes((int)r.ReadUInt32());
                        a.Objs.Add(o);
                    }
                    v.Assets.Add(a);
                }
                uint nr = r.ReadUInt32();
                for (uint i = 0; i < nr; i++)
                {
                    var p = new RessPatch(); p.Name = ReadStr(r); p.Size = (long)r.ReadUInt64();
                    uint n = r.ReadUInt32();
                    for (uint j = 0; j < n; j++) { var g = new Region(); g.Off = (long)r.ReadUInt64(); g.Data = r.ReadBytes((int)r.ReadUInt32()); p.Regions.Add(g); }
                    v.Ress.Add(p);
                }
            }
            return v;
        }
    }

    static class Motor
    {
        static void WriteStr(BinaryWriter w, string s) { byte[] b = Encoding.UTF8.GetBytes(s); w.Write((ushort)b.Length); w.Write(b); }
        static string ReadStr(BinaryReader r) { int n = r.ReadUInt16(); return Encoding.UTF8.GetString(r.ReadBytes(n)); }
        static ulong ReadBE64(byte[] b, int o) { ulong v = 0; for (int i = 0; i < 8; i++) v = (v << 8) | b[o + i]; return v; }
        static byte[] BE64(ulong v) { byte[] b = new byte[8]; for (int i = 7; i >= 0; i--) { b[i] = (byte)(v & 0xFF); v >>= 8; } return b; }
        static bool Eq(byte[] a, byte[] b) { if (a.Length != b.Length) return false; for (int i = 0; i < a.Length; i++) if (a[i] != b[i]) return false; return true; }
        static byte[] ReadAt(FileStream f, long off, int len)
        {
            f.Seek(off, SeekOrigin.Begin); byte[] b = new byte[len]; int got = 0;
            while (got < len) { int n = f.Read(b, got, len - got); if (n <= 0) throw new IOException("Beklenmeyen dosya sonu"); got += n; }
            return b;
        }

        public static bool Kurulu(string oyun) { return File.Exists(Path.Combine(Path.Combine(oyun, Sabit.BackupDir), Sabit.BackupFile)); }

        /// Oyun dosyaları yamanın beklediği orijinal sürümle aynı mı? (hiçbir şeye yazmaz)
        public static string SurumKontrol(string oyun, YamaVerisi v)
        {
            string data = Path.Combine(oyun, "ved_Data");
            foreach (var a in v.Assets)
            {
                string p = Path.Combine(data, a.Name);
                if (!File.Exists(p)) return "Dosya bulunamadı: " + a.Name;
                using (var f = new FileStream(p, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                {
                    if (f.Length != a.OrigSize || !Eq(ReadAt(f, 0, 48), a.OrigHeader)) return "Farklı sürüm: " + a.Name;
                    foreach (var o in a.Objs) if (!Eq(ReadAt(f, o.Off, 20), o.Orig20)) return "Farklı sürüm: " + a.Name;
                }
            }
            foreach (var p in v.Ress)
            {
                var fi = new FileInfo(Path.Combine(data, p.Name));
                if (!fi.Exists || fi.Length != p.Size) return "Farklı sürüm: " + p.Name;
            }
            return null;
        }

        public static void Kur(string oyun, YamaVerisi v, Action<int, string> ilerleme)
        {
            string data = Path.Combine(oyun, "ved_Data");
            string hata = SurumKontrol(oyun, v);
            if (hata != null) throw new Exception("Oyun sürümü bu yamayla uyuşmuyor. (" + hata + ")");

            ilerleme(10, "Orijinal dosyaların yedeği alınıyor...");
            string bdir = Path.Combine(oyun, Sabit.BackupDir); Directory.CreateDirectory(bdir);
            string tmp = Path.Combine(bdir, Sabit.BackupFile + ".tmp");
            using (var w = new BinaryWriter(File.Create(tmp)))
            {
                w.Write(Encoding.ASCII.GetBytes("VEDBK1"));
                w.Write((uint)v.Assets.Count);
                foreach (var a in v.Assets)
                {
                    WriteStr(w, a.Name); w.Write((ulong)a.OrigSize); w.Write(a.OrigHeader); w.Write((uint)a.Objs.Count);
                    foreach (var o in a.Objs) { w.Write((ulong)o.Off); w.Write(o.Orig20); }
                }
                w.Write((uint)v.Ress.Count);
                foreach (var p in v.Ress)
                {
                    WriteStr(w, p.Name); w.Write((ulong)p.Size); w.Write((uint)p.Regions.Count);
                    using (var f = new FileStream(Path.Combine(data, p.Name), FileMode.Open, FileAccess.Read, FileShare.Read))
                        foreach (var g in p.Regions) { w.Write((ulong)g.Off); w.Write((uint)g.Data.Length); w.Write(ReadAt(f, g.Off, g.Data.Length)); }
                }
            }
            string bfile = Path.Combine(bdir, Sabit.BackupFile);
            if (File.Exists(bfile)) File.Delete(bfile);
            File.Move(tmp, bfile);

            int toplam = v.Assets.Count + v.Ress.Count, sira = 0;
            foreach (var a in v.Assets)
            {
                ilerleme(20 + 70 * sira++ / toplam, "Metinler yazılıyor: " + a.Name);
                using (var f = new FileStream(Path.Combine(data, a.Name), FileMode.Open, FileAccess.ReadWrite, FileShare.None))
                {
                    ulong dataOffset = ReadBE64(a.OrigHeader, 32);
                    long end = f.Length;
                    foreach (var o in a.Objs)
                    {
                        long pos = (end + 15) & ~15L;
                        f.Seek(end, SeekOrigin.Begin); f.Write(new byte[pos - end], 0, (int)(pos - end));
                        f.Write(o.Data, 0, o.Data.Length); end = pos + o.Data.Length;
                        f.Seek(o.Off + 8, SeekOrigin.Begin);
                        f.Write(BitConverter.GetBytes((long)pos - (long)dataOffset), 0, 8);
                        f.Write(BitConverter.GetBytes((uint)o.Data.Length), 0, 4);
                    }
                    long fin = (end + 15) & ~15L;
                    f.Seek(end, SeekOrigin.Begin); f.Write(new byte[fin - end], 0, (int)(fin - end));
                    f.Seek(24, SeekOrigin.Begin); f.Write(BE64((ulong)fin), 0, 8);
                }
            }
            foreach (var p in v.Ress)
            {
                ilerleme(20 + 70 * sira++ / toplam, "Yazı tipleri yazılıyor: " + p.Name);
                using (var f = new FileStream(Path.Combine(data, p.Name), FileMode.Open, FileAccess.ReadWrite, FileShare.None))
                    foreach (var g in p.Regions) { f.Seek(g.Off, SeekOrigin.Begin); f.Write(g.Data, 0, g.Data.Length); }
            }
            ilerleme(100, "Kurulum tamamlandı.");
        }

        public static string Kaldir(string oyun, Action<int, string> ilerleme)
        {
            string data = Path.Combine(oyun, "ved_Data");
            string bfile = Path.Combine(Path.Combine(oyun, Sabit.BackupDir), Sabit.BackupFile);
            if (!File.Exists(bfile)) return "Yüklü bir Türkçe yama bulunamadı.";
            var uyarilar = new List<string>();
            ilerleme(10, "Yedek okunuyor...");
            using (var r = new BinaryReader(File.OpenRead(bfile)))
            {
                if (Encoding.ASCII.GetString(r.ReadBytes(6)) != "VEDBK1") throw new Exception("Yedek dosyası bozuk.");
                uint na = r.ReadUInt32();
                for (uint i = 0; i < na; i++)
                {
                    string name = ReadStr(r); long size = (long)r.ReadUInt64(); byte[] hdr = r.ReadBytes(48); uint n = r.ReadUInt32();
                    var ents = new List<KeyValuePair<long, byte[]>>();
                    for (uint j = 0; j < n; j++) { long off = (long)r.ReadUInt64(); ents.Add(new KeyValuePair<long, byte[]>(off, r.ReadBytes(20))); }
                    ilerleme(20 + (int)(30 * i / Math.Max(1, na)), "Geri yükleniyor: " + name);
                    using (var f = new FileStream(Path.Combine(data, name), FileMode.Open, FileAccess.ReadWrite, FileShare.None))
                    {
                        byte[] cur = ReadAt(f, 0, 48);
                        bool yamali = f.Length > size && (long)ReadBE64(cur, 24) == f.Length;
                        if (!yamali) { uyarilar.Add(name); continue; }
                        foreach (var e in ents) { f.Seek(e.Key, SeekOrigin.Begin); f.Write(e.Value, 0, 20); }
                        f.Seek(0, SeekOrigin.Begin); f.Write(hdr, 0, 48); f.SetLength(size);
                    }
                }
                uint nr = r.ReadUInt32();
                for (uint i = 0; i < nr; i++)
                {
                    string name = ReadStr(r); long size = (long)r.ReadUInt64(); uint n = r.ReadUInt32();
                    ilerleme(50 + (int)(45 * i / Math.Max(1, nr)), "Geri yükleniyor: " + name);
                    string p = Path.Combine(data, name);
                    bool ok = new FileInfo(p).Length == size;
                    if (!ok) uyarilar.Add(name);
                    FileStream f = ok ? new FileStream(p, FileMode.Open, FileAccess.ReadWrite, FileShare.None) : null;
                    try
                    {
                        for (uint j = 0; j < n; j++)
                        {
                            long off = (long)r.ReadUInt64(); byte[] b = r.ReadBytes((int)r.ReadUInt32());
                            if (ok) { f.Seek(off, SeekOrigin.Begin); f.Write(b, 0, b.Length); }
                        }
                    }
                    finally { if (f != null) f.Dispose(); }
                }
            }
            File.Delete(bfile);
            try { Directory.Delete(Path.Combine(oyun, Sabit.BackupDir)); } catch { }
            ilerleme(100, "Kaldırma tamamlandı.");
            if (uyarilar.Count > 0)
                return "Yama kaldırıldı, ancak şu dosyalar oyun güncellemesiyle değişmiş ve atlandı: " + string.Join(", ", uyarilar.ToArray()) +
                       ". Gerekirse Steam'den dosya bütünlüğünü doğrulayın.";
            return "Türkçe yama kaldırıldı, orijinal dosyalar geri yüklendi.";
        }
    }

    // ---------------------------------------------------------------- oyun bulma ve orijinallik denetimi
    static class Denetim
    {
        public static bool OyunKlasoruMu(string p)
        {
            return !string.IsNullOrEmpty(p) && File.Exists(Path.Combine(p, "ved.exe")) && File.Exists(Path.Combine(p, "ved_Data\\resources.assets"));
        }

        static List<string> SteamKutuphaneleri()
        {
            var lib = new List<string>();
            string[] anahtarlar = { @"HKEY_CURRENT_USER\Software\Valve\Steam", @"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Valve\Steam", @"HKEY_LOCAL_MACHINE\SOFTWARE\Valve\Steam" };
            foreach (string k in anahtarlar)
            {
                foreach (string ad in new string[] { "SteamPath", "InstallPath" })
                {
                    object o = null; try { o = Registry.GetValue(k, ad, null); } catch { }
                    if (o != null) lib.Add(o.ToString().Replace('/', '\\'));
                }
            }
            lib.Add(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "Steam"));
            var ek = new List<string>();
            foreach (string s in lib)
            {
                string vdf = Path.Combine(s, "steamapps\\libraryfolders.vdf");
                if (!File.Exists(vdf)) continue;
                try
                {
                    foreach (Match m in Regex.Matches(File.ReadAllText(vdf), "\"path\"\\s+\"([^\"]+)\""))
                        ek.Add(m.Groups[1].Value.Replace("\\\\", "\\"));
                }
                catch { }
            }
            lib.AddRange(ek);
            var sonuc = new List<string>();
            foreach (string s in lib) { string t = s.TrimEnd('\\'); bool var_ = false; foreach (string u in sonuc) if (string.Equals(u, t, StringComparison.OrdinalIgnoreCase)) var_ = true; if (!var_ && Directory.Exists(t)) sonuc.Add(t); }
            return sonuc;
        }

        public static string OyunuBul()
        {
            foreach (string lib in SteamKutuphaneleri())
            {
                string acf = Path.Combine(lib, "steamapps\\appmanifest_" + Sabit.AppId + ".acf");
                if (File.Exists(acf))
                {
                    string dir = AcfDeger(File.ReadAllText(acf), "installdir");
                    if (dir != null)
                    {
                        string p = Path.Combine(Path.Combine(lib, "steamapps\\common"), dir);
                        if (OyunKlasoruMu(p)) return p;
                    }
                }
            }
            string exeDir = Path.GetDirectoryName(Application.ExecutablePath);
            if (OyunKlasoruMu(exeDir)) return exeDir;
            return null;
        }

        static string AcfDeger(string acf, string anahtar)
        {
            Match m = Regex.Match(acf, "\"" + anahtar + "\"\\s+\"([^\"]*)\"");
            return m.Success ? m.Groups[1].Value : null;
        }

        static string Sha256(string yol)
        {
            using (var s = File.OpenRead(yol)) using (var h = SHA256.Create())
            {
                var sb = new StringBuilder();
                foreach (byte b in h.ComputeHash(s)) sb.Append(b.ToString("X2"));
                return sb.ToString();
            }
        }

        /// null = orijinal Steam kopyası; aksi hâlde neden
        public static string SteamKopyasiMi(string oyun)
        {
            // 1) Steam kütüphanesi içinde, geçerli appmanifest kaydıyla kurulu mu?
            DirectoryInfo common = Directory.GetParent(oyun.TrimEnd('\\'));
            if (common == null || !string.Equals(common.Name, "common", StringComparison.OrdinalIgnoreCase) ||
                common.Parent == null || !string.Equals(common.Parent.Name, "steamapps", StringComparison.OrdinalIgnoreCase))
                return "Oyun bir Steam kütüphanesi içinde kurulu değil.";
            string acfYol = Path.Combine(common.Parent.FullName, "appmanifest_" + Sabit.AppId + ".acf");
            if (!File.Exists(acfYol)) return "Steam kurulum kaydı (appmanifest) bulunamadı.";
            string acf = File.ReadAllText(acfYol);
            if (!string.Equals(AcfDeger(acf, "installdir"), new DirectoryInfo(oyun).Name, StringComparison.OrdinalIgnoreCase))
                return "Steam kurulum kaydı bu klasörle eşleşmiyor.";
            if (AcfDeger(acf, "StateFlags") != "4" || acf.IndexOf("\"" + Sabit.DepotId + "\"", StringComparison.Ordinal) < 0)
                return "Steam kurulumu tamamlanmamış ya da güncelleme bekliyor. Steam'de oyunu güncelleyip tekrar deneyin.";
            // 2) Steam istemcisi kurulu mu?
            string steamRoot = common.Parent.Parent.FullName;
            bool steamVar = File.Exists(Path.Combine(steamRoot, "steam.exe"));
            if (!steamVar) foreach (string lib in SteamKutuphaneleri()) if (File.Exists(Path.Combine(lib, "steam.exe"))) steamVar = true;
            if (!steamVar) return "Steam istemcisi bulunamadı.";
            // 3) Emülatör / kırık sürüm kalıntıları
            foreach (string kok in new string[] { oyun, Path.Combine(oyun, "ved_Data\\Plugins\\x86_64"), Path.Combine(oyun, "ved_Data\\Plugins") })
            {
                if (!Directory.Exists(kok)) continue;
                foreach (string d in Sabit.YasakliDosyalar) if (File.Exists(Path.Combine(kok, d))) return "Değiştirilmiş oyun dosyası tespit edildi: " + d;
                foreach (string d in Sabit.YasakliKlasorler) if (Directory.Exists(Path.Combine(kok, d))) return "Değiştirilmiş oyun klasörü tespit edildi: " + d;
            }
            // 4) Çekirdek dosyalar Steam'deki orijinalleriyle aynı mı?
            foreach (string[] od in Sabit.OrijinalDosyalar)
            {
                string p = Path.Combine(oyun, od[0]);
                if (!File.Exists(p)) return "Eksik oyun dosyası: " + od[0];
                if (Sha256(p) != od[1]) return "Oyun dosyası orijinal değil ya da farklı sürüm: " + Path.GetFileName(od[0]);
            }
            return null;
        }
    }

    // ---------------------------------------------------------------- arayüz
    class AnaForm : Form
    {
        static readonly Color Arka = Color.FromArgb(18, 18, 20), Panel_ = Color.FromArgb(30, 30, 34), Yazi = Color.FromArgb(235, 235, 235),
                              Soluk = Color.FromArgb(150, 150, 155), Kirmizi = Color.FromArgb(227, 10, 23), Yesil = Color.FromArgb(80, 200, 120), Sari = Color.FromArgb(240, 190, 60);
        TextBox yolKutu, gunluk; Button gozat, kurBtn, kaldirBtn; ProgressBar bar;
        Label[] durum = new Label[4];
        YamaVerisi veri; string oyun; bool mesgul; string otomatikIslem;

        public AnaForm(string oyunArg, string islemArg)
        {
            otomatikIslem = islemArg;
            Text = "Ved: Recure Türkçe Yama " + Sabit.Surum;
            FormBorderStyle = FormBorderStyle.FixedSingle; MaximizeBox = false; StartPosition = FormStartPosition.CenterScreen;
            ClientSize = new Size(620, 604); BackColor = Arka; ForeColor = Yazi; Font = new Font("Segoe UI", 9.5f);
            try { Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath); } catch { }

            Image banner = null;
            try { banner = Image.FromStream(Assembly.GetExecutingAssembly().GetManifestResourceStream("banner.png")); } catch { }
            var ust = new Panel { Location = new Point(0, 0), Size = new Size(620, 170), BackColor = Color.Black };
            ust.Paint += delegate (object s, PaintEventArgs e)
            {
                var g = e.Graphics;
                g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
                if (banner != null) g.DrawImage(banner, new Rectangle(0, 0, ust.Width, ust.Height));
                else g.DrawString("VED: RECURE", new Font("Segoe UI Black", 22f, FontStyle.Bold), Brushes.White, 22, 30);
                g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.AntiAliasGridFit;
                g.DrawString("TÜRKÇE YAMA", new Font("Segoe UI Black", 13f, FontStyle.Bold), new SolidBrush(Kirmizi), 24, 112);
                g.DrawString("sürüm " + Sabit.Surum + "  •  hazırlayan: " + Sabit.Yapimci, new Font("Segoe UI Semibold", 9.5f), Brushes.Gainsboro, 26, 138);
            };
            Controls.Add(ust);

            Controls.Add(new Label { Text = "Oyun klasörü", Location = new Point(22, 186), AutoSize = true, ForeColor = Soluk });
            yolKutu = new TextBox { Location = new Point(24, 208), Size = new Size(470, 26), BackColor = Panel_, ForeColor = Yazi, BorderStyle = BorderStyle.FixedSingle, ReadOnly = true };
            Controls.Add(yolKutu);
            gozat = DugmeYap("Gözat...", new Point(504, 206), new Size(92, 29), Panel_);
            gozat.Click += delegate { KlasorSec(); };
            Controls.Add(gozat);

            string[] basliklar = { "Oyun bulundu", "Orijinal Steam kopyası", "Sürüm uyumluluğu", "Yama durumu" };
            for (int i = 0; i < 4; i++)
            {
                Controls.Add(new Label { Text = basliklar[i], Location = new Point(24, 254 + i * 28), AutoSize = true });
                durum[i] = new Label { Text = "—", Location = new Point(230, 254 + i * 28), Size = new Size(370, 22), ForeColor = Soluk };
                Controls.Add(durum[i]);
            }

            kurBtn = DugmeYap("YAMAYI KUR", new Point(24, 376), new Size(280, 44), Kirmizi);
            kurBtn.Font = new Font("Segoe UI", 11f, FontStyle.Bold);
            kurBtn.Click += delegate { IslemBaslat(true); };
            kaldirBtn = DugmeYap("Yamayı Kaldır", new Point(316, 376), new Size(280, 44), Panel_);
            kaldirBtn.Click += delegate { IslemBaslat(false); };
            Controls.Add(kurBtn); Controls.Add(kaldirBtn);

            bar = new ProgressBar { Location = new Point(24, 434), Size = new Size(572, 12), Style = ProgressBarStyle.Continuous };
            Controls.Add(bar);
            gunluk = new TextBox { Location = new Point(24, 456), Size = new Size(572, 108), Multiline = true, ReadOnly = true, ScrollBars = ScrollBars.Vertical,
                                   BackColor = Panel_, ForeColor = Soluk, BorderStyle = BorderStyle.None, Font = new Font("Consolas", 9f) };
            Controls.Add(gunluk);
            Controls.Add(new Label { Text = "Türkçe yama: " + Sabit.Yapimci + "  •  Discord: " + Sabit.Discord + "  •  Gayriresmî hayran çevirisidir.", Location = new Point(22, 574),
                                     AutoSize = true, ForeColor = Color.FromArgb(110, 110, 115), Font = new Font("Segoe UI", 8.5f) });

            kurBtn.Enabled = kaldirBtn.Enabled = false;
            Shown += delegate
            {
                Log("Ved: Recure Türkçe Yama " + Sabit.Surum + " — hazırlayan: " + Sabit.Yapimci + " (Discord: " + Sabit.Discord + ")");
                Log("Yama verisi yükleniyor...");
                try { veri = YamaVerisi.Yukle(); } catch (Exception ex) { Log("HATA: " + ex.Message); return; }
                string yol = Denetim.OyunKlasoruMu(oyunArg) ? oyunArg : Denetim.OyunuBul();
                if (yol == null) { Log("Oyun otomatik bulunamadı. 'Gözat...' ile ved.exe'nin bulunduğu klasörü seçin."); Durum(0, false, "Bulunamadı"); }
                else OyunAyarla(yol);
            };
        }

        Button DugmeYap(string yazi, Point konum, Size boyut, Color renk)
        {
            var b = new Button { Text = yazi, Location = konum, Size = boyut, BackColor = renk, ForeColor = Color.White, FlatStyle = FlatStyle.Flat, Cursor = Cursors.Hand };
            b.FlatAppearance.BorderColor = Color.FromArgb(70, 70, 75); b.FlatAppearance.BorderSize = 1;
            return b;
        }

        void Log(string s) { gunluk.AppendText(DateTime.Now.ToString("HH:mm:ss") + "  " + s + Environment.NewLine); }
        void Durum(int i, bool? ok, string yazi)
        {
            durum[i].Text = (ok == true ? "✔  " : ok == false ? "✖  " : "•  ") + yazi;
            durum[i].ForeColor = ok == true ? Yesil : ok == false ? Kirmizi : Sari;
        }

        void KlasorSec()
        {
            using (var d = new FolderBrowserDialog { Description = "Ved: Recure'un kurulu olduğu klasörü seçin (ved.exe'nin bulunduğu klasör)" })
            {
                if (d.ShowDialog(this) != DialogResult.OK) return;
                if (!Denetim.OyunKlasoruMu(d.SelectedPath)) { MessageBox.Show(this, "Seçilen klasörde ved.exe ve ved_Data bulunamadı.", Text, MessageBoxButtons.OK, MessageBoxIcon.Warning); return; }
                OyunAyarla(d.SelectedPath);
            }
        }

        void OyunAyarla(string yol)
        {
            oyun = yol; yolKutu.Text = yol; Durum(0, true, "Bulundu");
            kurBtn.Enabled = kaldirBtn.Enabled = gozat.Enabled = false;
            Durum(1, null, "Denetleniyor..."); Durum(2, null, "Denetleniyor..."); Durum(3, null, "Denetleniyor...");
            ThreadPool.QueueUserWorkItem(delegate
            {
                string steam = null, surum = null; bool kurulu = false; Exception hata = null;
                try
                {
                    steam = Denetim.SteamKopyasiMi(yol);
                    kurulu = Motor.Kurulu(yol);
                    if (!kurulu) surum = Motor.SurumKontrol(yol, veri);
                }
                catch (Exception ex) { hata = ex; }
                BeginInvoke((MethodInvoker)delegate
                {
                    gozat.Enabled = true;
                    if (hata != null) { Log("HATA: " + hata.Message); return; }
                    Durum(1, steam == null, steam == null ? "Doğrulandı" : "Doğrulanamadı");
                    if (steam != null) Log("Orijinallik denetimi: " + steam);
                    if (kurulu) { Durum(2, true, "Uyumlu"); Durum(3, true, "Kurulu"); }
                    else
                    {
                        Durum(2, surum == null, surum == null ? "Uyumlu (Steam build 25483973)" : "Uyumsuz");
                        if (surum != null) Log("Sürüm denetimi: " + surum + ". Oyun güncellenmiş olabilir; yamanın yeni sürümünü bekleyin.");
                        Durum(3, null, "Kurulu değil");
                    }
                    kurBtn.Enabled = steam == null && (kurulu || surum == null);
                    kaldirBtn.Enabled = kurulu;
                    kurBtn.Text = kurulu ? "YENİDEN KUR" : "YAMAYI KUR";
                    if (steam == null) Log("Hazır.");
                    else Log("Bu yama yalnızca Steam'den edinilmiş orijinal Ved: Recure kopyasına kurulabilir.");
                    if (otomatikIslem != null)
                    {
                        string i = otomatikIslem; otomatikIslem = null;
                        if (i == "kur" && kurBtn.Enabled) IslemBaslat(true);
                        else if (i == "kaldir" && kaldirBtn.Enabled) IslemBaslat(false);
                    }
                });
            });
        }

        void IslemBaslat(bool kur)
        {
            if (mesgul || oyun == null) return;
            if (Process.GetProcessesByName("ved").Length > 0)
            {
                MessageBox.Show(this, "Oyun şu anda açık. Lütfen önce oyunu kapatın.", Text, MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            mesgul = true; kurBtn.Enabled = kaldirBtn.Enabled = gozat.Enabled = false; bar.Value = 0;
            ThreadPool.QueueUserWorkItem(delegate
            {
                string sonuc = null; Exception hata = null;
                Action<int, string> ilerleme = delegate (int y, string m)
                {
                    BeginInvoke((MethodInvoker)delegate { bar.Value = Math.Max(0, Math.Min(100, y)); Log(m); });
                };
                try
                {
                    if (kur)
                    {
                        string steam = Denetim.SteamKopyasiMi(oyun);
                        if (steam != null) throw new Exception("Bu yama yalnızca Steam'den edinilmiş orijinal kopyaya kurulabilir. (" + steam + ")");
                        if (Motor.Kurulu(oyun)) { ilerleme(5, "Önceki yama kaldırılıyor..."); Motor.Kaldir(oyun, delegate (int a, string b) { }); }
                        Motor.Kur(oyun, veri, ilerleme);
                        sonuc = "Kurulum tamamlandı!\n\nTürkçe yama: " + Sabit.Yapimci + " (Discord: " + Sabit.Discord + ")\n\nOyunda Ayarlar > Dil bölümünden \"Türkçe\" seçeneğini seçin.\n\nNot: Steam'de \"dosya bütünlüğünü doğrula\" işlemi yamayı siler.";
                    }
                    else sonuc = Motor.Kaldir(oyun, ilerleme);
                }
                catch (Exception ex) { hata = ex; }
                BeginInvoke((MethodInvoker)delegate
                {
                    mesgul = false;
                    if (hata is UnauthorizedAccessException || (hata != null && hata.InnerException is UnauthorizedAccessException))
                    {
                        Log("HATA: Dosyalara yazma izni yok.");
                        if (MessageBox.Show(this, "Oyun dosyalarına yazma izni yok. Program yönetici olarak yeniden başlatılsın mı?", Text,
                                            MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes)
                        {
                            try
                            {
                                Process.Start(new ProcessStartInfo(Application.ExecutablePath, "--oyun \"" + oyun + "\" --islem " + (kur ? "kur" : "kaldir")) { Verb = "runas", UseShellExecute = true });
                                Close(); return;
                            }
                            catch { Log("Yönetici izni verilmedi."); }
                        }
                    }
                    else if (hata != null)
                    {
                        Log("HATA: " + hata.Message);
                        MessageBox.Show(this, hata.Message, Text, MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                    else
                    {
                        MessageBox.Show(this, sonuc, Text, MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                    OyunAyarla(oyun);
                });
            });
        }
    }

    static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            string oyun = null, islem = null;
            for (int i = 0; i + 1 < args.Length; i++)
            {
                if (args[i] == "--oyun") oyun = args[i + 1];
                if (args[i] == "--islem") islem = args[i + 1];
            }
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new AnaForm(oyun, islem));
        }
    }
}

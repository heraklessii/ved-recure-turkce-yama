using System;
namespace VedTurkceYama {
  static class TestMain {
    static void Main(string[] a) {
      Console.OutputEncoding = System.Text.Encoding.UTF8;
      string oyun = Denetim.OyunuBul();
      Console.WriteLine("Oyun: " + oyun);
      Console.WriteLine("Steam denetimi: " + (Denetim.SteamKopyasiMi(oyun) ?? "OK"));
      var v = YamaVerisi.Yukle();
      Console.WriteLine("Kurulu: " + Motor.Kurulu(oyun));
      if (a.Length > 0 && a[0] == "kur") {
        Console.WriteLine("Surum: " + (Motor.SurumKontrol(oyun, v) ?? "OK"));
        Motor.Kur(oyun, v, delegate(int p, string m) { Console.WriteLine(p + "% " + m); });
      }
      if (a.Length > 0 && a[0] == "surum") { bool y; Console.WriteLine("GitHub son surum: " + Guncelleme.SonSurum() + " | denetim: " + (Guncelleme.Denetle(out y) ?? "GUNCEL")); }
      if (a.Length > 0 && a[0] == "denetle") Console.WriteLine("Eski yedek dosyalari: " + string.Join(", ", Motor.YedekDenetle(oyun).ToArray()));
      if (a.Length > 0 && a[0] == "kaldir") Console.WriteLine(Motor.Kaldir(oyun, delegate(int p, string m) { Console.WriteLine(p + "% " + m); }));
      if (a.Length > 1 && a[0] == "ekran") {
        var f = new AnaForm(null, null);
        f.StartPosition = System.Windows.Forms.FormStartPosition.Manual; f.Location = new System.Drawing.Point(-3000, 0);
        f.Show(); System.Windows.Forms.Application.DoEvents(); System.Threading.Thread.Sleep(4000); System.Windows.Forms.Application.DoEvents();
        var b = new System.Drawing.Bitmap(f.Width, f.Height); f.DrawToBitmap(b, new System.Drawing.Rectangle(0,0,f.Width,f.Height));
        b.Save(a[1]); f.Close();
      }
      if (a.Length > 0 && a[0] == "sahte") {   // emülatör kalıntısı varken denetim reddetmeli
        string f = System.IO.Path.Combine(oyun, "steam_appid.txt");
        System.IO.File.WriteAllText(f, "3255500");
        Console.WriteLine("Sahte kopya denetimi: " + (Denetim.SteamKopyasiMi(oyun) ?? "OK (HATALI!)"));
        System.IO.File.Delete(f);
      }
    }
  }
}

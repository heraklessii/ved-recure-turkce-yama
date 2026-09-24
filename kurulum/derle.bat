@echo off
rem turkce.yama (pack.py ciktisi) bu klasore kopyalanmis olmali
cd /d "%~dp0"
"%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:winexe /optimize+ /codepage:65001 /out:VedTurkceYama.exe /win32icon:ikon.ico /win32manifest:app.manifest /resource:turkce.yama,turkce.yama /resource:banner.png,banner.png /r:System.Windows.Forms.dll /r:System.Drawing.dll VedTurkceYama.cs

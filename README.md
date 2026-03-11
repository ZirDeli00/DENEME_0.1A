# Hakan ÇELİK Yapay Zeka Sohbet

Bu proje, tek bir HTML dosyasıyla çalışan ve yerel "beyin" + internet destekli araştırma yetenekleri sunan bir sohbet arayüzüdür.

## Dosyalar
- `Hakan_CELIK_Chat.html`: Modern sohbet arayüzü + karar veren yerel beyin + web araştırma + dosya/fotoğraf ekleme.
- `launcher.py`: HTML dosyasını varsayılan tarayıcıda açar.
- `build_exe.bat`: Windows'ta `launcher.py` dosyasından `HakanCELIKChat.exe` üretir.

## Öne Çıkan Özellikler
- Sorunun tipini analiz eden yerel "beyin" (intent + ihtiyaç analizi)
- İnternet araması gerekip gerekmediğine otomatik karar verme
- İnternetten bulunan cevabı yeni sekme açmadan sohbet ekranında gösterme
- Kullanıcı adı hafızası, saat/tarih, temel matematik
- Dosya ve fotoğraf yükleme, mesaja ekli gösterim

## HTML ile açma
Windows'ta `Hakan_CELIK_Chat.html` dosyasına çift tıklayın.

## EXE ile açma (Windows)
1. Python kurulu olmalı.
2. `build_exe.bat` dosyasını çalıştırın.
3. Oluşan `dist/HakanCELIKChat.exe` dosyasını çalıştırarak sohbet uygulamasını açın.

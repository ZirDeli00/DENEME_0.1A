# Subway 3D Runner

Bu proje, **Subway Surfers benzeri pseudo-3D (perspektif) bir koşu oyunu** sunar.

## Özellikler

- Ana menü: **Oyna**, **Ayarlar**, **Oynanış**
- 3 şeritli perspektif (3D hissi veren) yol
- Engel ve coin mekaniği
- Zıplama + 3 can sistemi
- Can azalınca çarpma animasyonu (flash/shake)
- Ayarlar ekranında mp3 yükleme:
  - Sürükle-bırak (tkinterdnd2 varsa)
  - Dosya seç butonu (yedek yöntem)

## Hızlı Çalıştırma (Windows)

1. Python 3 kurulu olsun.
2. `run_game.bat` dosyasına çift tıkla.

## Kontroller

- `A` / `D` veya `←` / `→`: şerit değiştir
- `W`, `↑` veya `Space`: zıpla
- `R`: oyun bittiyse yeniden başlat

## EXE Oluşturma

1. `build_exe.bat` dosyasına çift tıkla.
2. İşlem bitince `dist/SubwayCmdGame.exe` oluşur.

## Notlar

- Müzik çalması için `pygame` gerekir.
- Sürükle-bırak için `tkinterdnd2` gerekir.
- Bu paketler yoksa oyun çalışır; sadece ilgili özellikler kısıtlı olur.

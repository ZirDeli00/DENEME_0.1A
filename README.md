# Subway 3D Runner

Bu proje, **Subway Surfers benzeri pseudo-3D (perspektif) bir koşu oyunu** sunar.

## Özellikler

- 3 şeritli perspektif (3D hissi veren) yol
- Engel ve coin toplama mekaniği
- Zıplama hareketi
- **3 can hakkı**
- Can azalınca **çarpma animasyonu** (ekran flash + kısa shake)
- Skor ve en iyi skor takibi

## Hızlı Çalıştırma (Windows)

1. Bilgisayarında Python 3 kurulu olsun.
2. `run_game.bat` dosyasına çift tıkla.

## Kontroller

- `A` / `D` veya `←` / `→`: şerit değiştir
- `W`, `↑` veya `Space`: zıpla
- `R`: oyun bitince yeniden başlat

## EXE Oluşturma

1. `build_exe.bat` dosyasına çift tıkla.
2. İşlem bitince `dist/SubwayCmdGame.exe` oluşur.
3. Bu `.exe` dosyasına çift tıklayarak oyunu başlatabilirsin.

> Not: Oyun Tkinter kullandığı için standart Python kurulumunda ek paket gerektirmez.

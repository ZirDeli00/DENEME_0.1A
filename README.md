# Basit Flipy Bird

Bu oyun tek dosyalık bir web oyunudur (`index.html`).

## 1) En kolay yöntem (sunucusuz)

- `index.html` dosyasına çift tıklayıp tarayıcıda aç.

> Not: Bazı tarayıcı/kurulumlarda yerel dosya (`file://`) kısıtları olabilir. Sorun yaşarsan aşağıdaki CMD yöntemi en sağlıklısıdır.

## 2) Windows CMD ile çalıştırma (önerilen)

### Gereken
- Bilgisayarda Python kurulu olmalı (`python --version` çalışmalı).

### Adımlar
1. CMD aç.
2. Proje klasörüne gir:
   ```cmd
   cd C:\path\to\DENEME_0.1A
   ```
3. Basit sunucu başlat:
   ```cmd
   python -m http.server 4173
   ```
4. Tarayıcıdan aç:
   - `http://localhost:4173`

Sunucuyu kapatmak için CMD penceresinde `Ctrl + C`.

## 3) Tek komutluk Windows yardımcı script

Repo içinde `start_windows.bat` dosyası var. CMD'de proje klasöründe şunu çalıştır:

```cmd
start_windows.bat
```

Bu script:
- Python kontrolü yapar,
- `http://localhost:4173` adresini açar,
- Sunucuyu başlatır.

## Oyun kontrolleri
- `Space` veya mouse/touch tık: zıpla
- `R`: oyun bitince yeniden başlat

## Dosyaları "link gibi" paylaşma (ZIP)

Doğrudan buradan internet linki üretemiyorsak en pratik yöntem ZIP oluşturup Drive/WeTransfer'a yüklemek.

### Windows CMD ile hızlı ZIP oluşturma

Proje klasöründe:

```cmd
package_for_share.bat
```

Bu komut `flipy-bird-package.zip` dosyası üretir. Sonra bu ZIP'i Google Drive / WeTransfer / Discord vb. yere yükleyip link paylaşabilirsin.


## ESC ile Ayarlar Menüsü
- Oyunda `ESC` tuşuna basınca ayarlar menüsü açılır/kapanır.
- Menüden müzik sesi ayarlanır.

## Spotify müziği hakkında
- İstediğin Spotify parçasının linki ayarlar menüsüne eklendi.
- Spotify teknik/politika sebepleriyle bu linkten oyunun içine direkt stream vermez.
- Oyunda müzik çalması için proje klasörüne `music.mp3` dosyası koyabilirsin (ayar menüsünden sesini kontrol edersin).

## Oyunu EXE olarak açma
1. Windows'ta proje klasöründe:
   ```cmd
   build_exe.bat
   ```
2. Oluşan dosya:
   - `dist\FlipyBird.exe`

`FlipyBird.exe` çalışınca oyunu tarayıcıda otomatik açar.

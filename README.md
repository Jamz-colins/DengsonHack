# DengsonHack v2.0.0

**DengsonHack** adalah *Terminal-Based OSINT Toolkit* berbasis Python dengan tampilan antarmuka CLI bertema Catppuccin Mocha untuk mengumpulkan informasi intelijen sumber terbuka (*Open-Source Intelligence*) secara cepat dari satu tempat.

- **Author:** Siro
- **GitHub:** [@musija](https://github.com/musija)
- **Version:** `2.0.0`

---

## Fitur Utama

1. **Information By Number**
   - Pencarian otomatis **Top 5 Google Search Results** dan menyimpannya ke `data/Google_Search_Results.json`.
   - Validasi nomor telepon menggunakan **Numverify API** (mendukung *API Key* milik masing-masing pengguna) atau mode *offline* otomatis menggunakan `phonenumbers`, lalu menyimpannya ke `data/Phone_Validation.json`.
   - Generator tautan langsung untuk pengecekan akun **WhatsApp** (`wa.me`) dan **Telegram** (`t.me`), serta pengecekan ketersediaan akun **Instagram**.
2. **Information By Username**
   - Pemindaian multi-thread secara bersamaan pada berbagai platform populer (GitHub, GitLab, Reddit, Steam, Instagram, TikTok, YouTube, Pinterest, Linktree, Chess.com).
3. **Information By Email**
   - Validasi format email, pengecekan *MX Record* domain melalui DNS resolver, pembuatan hash MD5, dan deteksi profil publik **Gravatar**.
4. **Information By IP**
   - Pelacakan geolokasi IP/domain, koordinat Google Maps, ISP, ASN, *Reverse DNS*, serta deteksi status Proxy/VPN/Hosting.
5. **Fetch YouTube Comments**
   - Pengambilan komentar terbaru dari URL video YouTube tanpa memerlukan kuota YouTube Data API key.
6. **Auto-Save JSON & Sapaan Perangkat**
   - Seluruh laporan tersimpan otomatis di folder `data/`, dan aplikasi akan menyapa pemilik perangkat (`user@hostname`) saat keluar dari program.

---

## Instalasi

### A. Arch Linux / CachyOS (Terminal Fish)

```fish
sudo pacman -Syu --needed git python python-pip python-virtualenv whois dnsutils
git clone [https://github.com/musija/DengsonHack.git](https://github.com/musija/DengsonHack.git)
cd DengsonHack

python -m venv .venv
source .venv/bin/activate.fish
pip install --upgrade pip
pip install -r requirements.txt
```

### B. Debian / Ubuntu / Kali Linux (Bash / Zsh)

```bash
sudo apt update && sudo apt install -y git python3 python3-pip python3-venv whois dnsutils
git clone [https://github.com/musija/DengsonHack.git](https://github.com/musija/DengsonHack.git)
cd DengsonHack

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Cara Menjalankan

Masuk ke direktori proyek, aktifkan *virtual environment* secara manual, jalankan `dengson.py`, lalu nonaktifkan kembali setelah selesai:

**Pada Fish Shell (CachyOS):**
```fish
cd ~/projects/DengsonHack
source .venv/bin/activate.fish
python dengson.py
# Setelah keluar dari menu:
deactivate
```

**Pada Bash / Zsh (Debian/Ubuntu):**
```bash
cd ~/projects/DengsonHack
source .venv/bin/activate
python3 dengson.py
# Setelah keluar dari menu:
deactivate
```

---

## Konfigurasi API Key (Numverify)

Untuk menggunakan fitur validasi nomor online pada menu **1 (Information By Number)**:
1. Daftar akun gratis di [numverify.com](https://numverify.com/) untuk mendapatkan *API Access Key*.
2. Saat menjalankan menu nomor telepon, tempelkan *API Key* milikmu ketika diminta di terminal.
3. Kunci akan disimpan secara lokal di `data/.user_apikey.json` pada perangkatmu sendiri (tidak ikut terunggah ke repositori publik). Jika tidak memiliki API key, cukup tekan **Enter** untuk menggunakan mode validasi *offline*.

---

## Disclaimer

Alat ini dibuat untuk tujuan edukasi, riset keamanan siber, dan pengumpulan informasi publik yang sah (*OSINT*). Segala bentuk penyalahgunaan di luar hukum yang berlaku sepenuhnya menjadi tanggung jawab pengguna.

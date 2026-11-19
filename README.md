<div align="center">

```text
    ____                                 __  __           __  
   / __ \___  ____  ____ __________  ____/ / / /___ ______/ /__
  / / / / _ \/ __ \/ __ `/ ___/ __ \/ __  / /_/ / __ `/ ___/ //_/
 / /_/ /  __/ / / / /_/ (__  ) /_/ / / / / __  / /_/ / /__/ ,<   
/_____/\___/_/ /_/\__, /____/\____/_/ /_/_/ /_/\__,_/\___/_/|_|  
                 /____/                                          

╔══════════════════════════════════════════════════════╗
║  Welcome to DengsonHack                              ║
║  Created By : Siro                                   ║
║  GitHub     : [https://github.com/Jamz-colins](https://github.com/Jamz-colins)         ║
║  Version    : 2.0.0                                  ║
╚══════════════════════════════════════════════════════╝
```

**DengsonHack — Terminal-Based OSINT Toolkit**  
*Gather intelligence from numbers, usernames, IPs & more - all in one place!*

[![Version](https://img.shields.io/badge/Version-2.0.0-a6e3a1?style=for-the-badge&labelColor=1e1e2e)](https://github.com/Jamz-colins/DengsonHack)
[![Author](https://img.shields.io/badge/Author-Siro-cba6f7?style=for-the-badge&labelColor=1e1e2e)](https://github.com/Jamz-colins)
[![Python](https://img.shields.io/badge/Python-3.10+-89b4fa?style=for-the-badge&logo=python&logoColor=89b4fa&labelColor=1e1e2e)](https://www.python.org/)
[![Shell](https://img.shields.io/badge/Shell-Fish_%7C_Bash-94e2d5?style=for-the-badge&logo=gnu-bash&logoColor=94e2d5&labelColor=1e1e2e)](#instalasi)
[![Theme](https://img.shields.io/badge/Palette-Catppuccin_Mocha-f5c2e7?style=for-the-badge&labelColor=1e1e2e)](#)

</div>

---

## `❯` Terminal Preview

```text
~/projects/DengsonHack
.venv ❯ python dengson.py

Please select an option:
1. Information By Number
2. Information By Username
3. Information By Email
4. Information By IP
5. Fetch YouTube Comments
6. Exit
Enter Your Choice: 1
Enter Phone Number to search: 0812xxxxxxxx

[FIND] Searching Google...
Google_Search_Results.json Saved in Data Folder
[+] Top 5 Results for '812xxxxxxxx':
...
================================================
Enter Your [http://numverify.com](http://numverify.com) API KEY:- ****************
[+] Validating phone number...
Phone_Validation.json Saved in Data Folder

TAKE A LOOK [0_0]
[+] Look For Whatsapp : [https://wa.me/62812xxxxxxxx](https://wa.me/62812xxxxxxxx)
[+] Look For Telegram : [https://t.me/+62812xxxxxxxx](https://t.me/+62812xxxxxxxx)
[CHECK] Checking Account On Instagram
```

---

## `❯` Modul & Fitur Utama

| Opsi | Modul | Kemampuan Intelijen |
| :--- | :--- | :--- |
| **`1`** | **Information By Number** | • Scraping **Top 5 Google Search Results** (`data/Google_Search_Results.json`)<br>• Validasi nomor via **Numverify API** (menggunakan *API Key* milik pengguna sendiri) atau mode *offline* (`data/Phone_Validation.json`)<br>• Tautan langsung **WhatsApp** (`wa.me`), **Telegram** (`t.me`), & pengecekan akun **Instagram** |
| **`2`** | **Information By Username** | • Pemindaian *multi-thread* serentak pada 10 platform populer (GitHub, GitLab, Reddit, Steam, Instagram, TikTok, YouTube, Pinterest, Linktree, Chess.com) |
| **`3`** | **Information By Email** | • Validasi format sintaks, pengecekan *MX Record* domain via DNS resolver, hash MD5, & deteksi profil publik **Gravatar** |
| **`4`** | **Information By IP** | • Pelacakan geolokasi IP/domain, koordinat Google Maps, ISP, ASN, *Reverse DNS*, & deteksi status Proxy/VPN/Hosting |
| **`5`** | **Fetch YouTube Comments** | • Ekstraksi komentar terbaru dari URL video YouTube tanpa memerlukan kuota YouTube Data API key |
| **`6`** | **Exit** | • Keluar dari sesi toolkit disertai panel sapaan otomatis ke pemilik perangkat (`user@hostname`) |

---

## `❯` Struktur Direktori

```text
~/projects/DengsonHack
├── .venv/               # Isolated Python virtual environment
├── config.py            # Identitas, palet Catppuccin Mocha, & manajemen JSON/API key
├── dengson.py           # Entry point utama & navigasi CLI
├── modules/
│   ├── __init__.py
│   ├── phone.py         # Modul 1: Number OSINT + Google Top 5 + Numverify
│   ├── username.py      # Modul 2: Multi-platform Username Scanner
│   ├── email_lookup.py  # Modul 3: Email MX Record & Gravatar Lookup
│   ├── ip_lookup.py     # Modul 4: IP Geolocation, ASN & Proxy Check
│   └── yt_comments.py   # Modul 5: YouTube Recent Comments Scraper
├── data/                # Hasil output JSON & API key lokal (diabaikan Git)
├── requirements.txt
└── README.md
```

---

## `❯` Instalasi

### 1. Arch Linux / CachyOS (`fish`)

```fish
~
❯ sudo pacman -Syu --needed git python python-pip python-virtualenv whois dnsutils

~
❯ mkdir -p ~/projects && cd ~/projects
❯ git clone [https://github.com/Jamz-colins/DengsonHack.git](https://github.com/Jamz-colins/DengsonHack.git)
❯ cd DengsonHack

~/projects/DengsonHack
❯ python -m venv .venv
❯ source .venv/bin/activate.fish

~/projects/DengsonHack
.venv ❯ pip install --upgrade pip
.venv ❯ pip install -r requirements.txt
.venv ❯ deactivate
```

### 2. Debian / Ubuntu / Kali Linux (`bash` / `zsh`)

```bash
sudo apt update && sudo apt install -y git python3 python3-pip python3-venv whois dnsutils
mkdir -p ~/projects && cd ~/projects
git clone [https://github.com/Jamz-colins/DengsonHack.git](https://github.com/Jamz-colins/DengsonHack.git)
cd DengsonHack

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

---

## `❯` Cara Menjalankan

Masuk ke direktori proyek, aktifkan *virtual environment* secara manual, jalankan `dengson.py`, lalu matikan kembali `venv` setelah selesai:

**Pada Fish Shell (CachyOS):**
```fish
~
❯ cd ~/projects/DengsonHack

~/projects/DengsonHack
❯ source .venv/bin/activate.fish

~/projects/DengsonHack
.venv ❯ python dengson.py

# Setelah keluar dari menu (Opsi 6):
~/projects/DengsonHack
.venv ❯ deactivate
```

**Pada Bash / Zsh (Debian / Ubuntu):**
```bash
cd ~/projects/DengsonHack
source .venv/bin/activate
python3 dengson.py

# Setelah keluar dari menu (Opsi 6):
deactivate
```

---

## `❯` Konfigurasi API Key Pengguna (Numverify)

Menu **1 (`Information By Number`)** dirancang agar setiap pengguna memakai kunci API miliknya sendiri tanpa terekspos di dalam kode sumber:

1. Buat akun gratis di [numverify.com](https://numverify.com/) dan salin *API Access Key* milikmu.
2. Jalankan menu **`1`** dan tempelkan *API Key* saat diminta di terminal.
3. Kunci akan disimpan secara lokal di `data/.user_apikey.json` (otomatis terblokir oleh `.gitignore` sehingga aman saat `git push`).
4. Jika tidak ingin menggunakan API online, cukup tekan **`Enter`** pada prompt API Key untuk beralih otomatis ke mode validasi *offline*.

---

## `❯` Disclaimer

Proyek ini dikembangkan untuk tujuan pembelajaran, riset keamanan siber, dan pengumpulan informasi publik yang sah (*OSINT*). Segala bentuk penyalahgunaan di luar ketentuan hukum yang berlaku sepenuhnya menjadi tanggung jawab pengguna.

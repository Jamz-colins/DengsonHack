from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from rich.console import Console
from rich.table import Table
from config import THEME, save_result

console = Console()

# Format: "Platform": ("URL_Template", [kata_kunci_jika_akun_tidak_ada])
PLATFORMS = {
    "GitHub": ("https://github.com/{}", ["not found"]),
    "GitLab": ("https://gitlab.com/{}", ["page not found", "sign in"]),
    "Reddit": ("https://www.reddit.com/user/{}/about.json", ["not found", '"error": 404']),
    "Steam": ("https://steamcommunity.com/id/{}", ["the specified profile could not be found"]),
    "Instagram": ("https://www.instagram.com/{}/", ["page isn't available", "page not found"]),
    "TikTok": ("https://www.tiktok.com/@{}", ["couldn't find this account"]),
    "YouTube": ("https://www.youtube.com/@{}", ["404 not found", "this page isn't available"]),
    "Pinterest": ("https://www.pinterest.com/{}/", ["user not found", "page not found"]),
    "Linktree": ("https://linktr.ee/{}", ["the page you’re looking for doesn’t exist", "page not found"]),
    "Chess.com": ("https://www.chess.com/member/{}", ["page not found", "oops!"]),
    "Medium": ("https://medium.com/@{}", ["404", "out of nothing, something"]),
    "Dev.to": ("https://dev.to/{}", ["page not found"]),
    "HuggingFace": ("https://huggingface.co/{}", ["sorry, we can't find the page"]),
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
}


def _check_site(platform: str, rule: tuple[str, list[str]], username: str):
    url_template, not_found_markers = rule
    check_url = url_template.format(username)
    display_url = check_url.replace("/about.json", "/")

    try:
        resp = requests.get(check_url, headers=HEADERS, timeout=7, allow_redirects=True)
        if resp.status_code == 200:
            lower_text = resp.text.lower()
            if any(marker in lower_text for marker in not_found_markers):
                return platform, display_url, False
            # Pastikan username tercantum di halaman agar tidak tertipu halaman login generik
            if username.lower() in lower_text:
                return platform, display_url, True
        return platform, display_url, False
    except requests.RequestException:
        return platform, display_url, False


def run():
    username = console.input(
        f"[{THEME['teal']}]Masukkan Username Target: [/]"
    ).strip()

    if not username:
        console.print(f"[{THEME['red']}]Username tidak boleh kosong.[/]\n")
        return

    found_accounts = {}
    table = Table(title=f"Hasil Pencarian Username: {username}", border_style=THEME["mauve"])
    table.add_column("Platform", style=THEME["blue"])
    table.add_column("Status", style=THEME["green"])
    table.add_column("URL Profil Aktif", style=THEME["teal"])

    with console.status(f"[{THEME['yellow']}]Memindai {len(PLATFORMS)} platform...[/]"):
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = [
                executor.submit(_check_site, name, rule, username)
                for name, rule in PLATFORMS.items()
            ]
            for future in as_completed(futures):
                platform, url, exists = future.result()
                if exists:
                    found_accounts[platform] = url
                    table.add_row(platform, "DITEMUKAN", url)

    if found_accounts:
        console.print(table)
        saved_path = save_result("username", username, found_accounts)
        console.print(f"[{THEME['subtext']}]Tersimpan di: {saved_path}[/]\n")
    else:
        console.print(f"[{THEME['yellow']}]Tidak ada profil publik yang cocok ditemukan.[/]\n")

from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from rich.console import Console
from rich.table import Table
from config import THEME, save_result

console = Console()

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "TikTok": "https://www.tiktok.com/@{}",
    "YouTube": "https://www.youtube.com/@{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Linktree": "https://linktr.ee/{}",
    "Chess.com": "https://www.chess.com/member/{}",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36"
}


def _check_site(platform: str, url_template: str, username: str):
    url = url_template.format(username)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=6, allow_redirects=True)
        if resp.status_code == 200:
            lower_text = resp.text.lower()
            if "page not found" not in lower_text and "couldn't find this account" not in lower_text:
                return platform, url, True
        return platform, url, False
    except requests.RequestException:
        return platform, url, False


def run():
    username = console.input(
        f"[{THEME['teal']}]Masukkan Username Target: [/]"
    ).strip()

    if not username:
        console.print(f"[{THEME['red']}]Username tidak boleh kosong.[/]")
        return

    found_accounts = {}
    table = Table(title=f"Hasil Pencarian Username: {username}", border_style=THEME["mauve"])
    table.add_column("Platform", style=THEME["blue"])
    table.add_column("Status", style=THEME["green"])
    table.add_column("URL Profil", style=THEME["teal"])

    with console.status(f"[{THEME['yellow']}]Memindai {len(PLATFORMS)} platform...[/]"):
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(_check_site, name, tpl, username)
                for name, tpl in PLATFORMS.items()
            ]
            for future in as_completed(futures):
                platform, url, exists = future.result()
                if exists:
                    found_accounts[platform] = url
                    table.add_row(platform, "DITEMUKAN", url)

    if found_accounts:
        console.print(table)
        saved_path = save_result("username", username, found_accounts)
        console.print(f"[{THEME['subtext']}]Tersimpan di: {saved_path}[/]")
    else:
        console.print(f"[{THEME['yellow']}]Tidak ada profil publik yang cocok ditemukan.[/]")
import hashlib
import re
import dns.resolver
import requests
from rich.console import Console
from rich.table import Table
from config import THEME, save_result

console = Console()


def run():
    email = console.input(
        f"[{THEME['teal']}]Masukkan Alamat Email Target: [/]"
    ).strip().lower()

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        console.print(f"[{THEME['red']}]Format email tidak valid.[/]")
        return

    domain = email.split("@")[1]
    mx_records = []
    try:
        answers = dns.resolver.resolve(domain, "MX")
        mx_records = [str(r.exchange).rstrip(".") for r in answers]
    except Exception:
        mx_records = []

    email_hash = hashlib.md5(email.encode("utf-8")).hexdigest()
    gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
    has_gravatar = False
    try:
        r = requests.get(gravatar_url, timeout=5)
        has_gravatar = r.status_code == 200
    except requests.RequestException:
        pass

    data = {
        "Email": email,
        "Domain": domain,
        "Mail Server Aktif": "Ya" if mx_records else "Tidak",
        "MX Records": ", ".join(mx_records) if mx_records else "-",
        "MD5 Hash": email_hash,
        "Gravatar Terdaftar": f"Ya ({gravatar_url})" if has_gravatar else "Tidak",
    }

    table = Table(title="Hasil OSINT Email", border_style=THEME["mauve"])
    table.add_column("Parameter", style=THEME["blue"])
    table.add_column("Informasi", style=THEME["green"])

    for k, v in data.items():
        table.add_row(k, str(v))

    console.print(table)
    saved_path = save_result("email", email, data)
    console.print(f"[{THEME['subtext']}]Tersimpan di: {saved_path}[/]")
import socket
import requests
from rich.console import Console
from rich.table import Table
from config import THEME, save_result

console = Console()


def run():
    target = console.input(
        f"[{THEME['teal']}]Masukkan IP Address atau Domain (kosongkan untuk IP sendiri): [/]"
    ).strip()

    endpoint = f"http://ip-api.com/json/{target}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,proxy,hosting,query"

    with console.status(f"[{THEME['yellow']}]Mengambil intelijen jaringan...[/]"):
        try:
            resp = requests.get(endpoint, timeout=8).json()
        except requests.RequestException as e:
            console.print(f"[{THEME['red']}]Gagal terhubung ke API: {e}[/]")
            return

    if resp.get("status") != "success":
        console.print(f"[{THEME['red']}]Gagal melacak target: {resp.get('message', 'Unknown error')}[/]")
        return

    ip_addr = resp.get("query", target)
    try:
        rdns = socket.gethostbyaddr(ip_addr)[0]
    except Exception:
        rdns = "-"

    data = {
        "IP Address": ip_addr,
        "Reverse DNS": rdns,
        "Negara": resp.get("country"),
        "Wilayah / Kota": f"{resp.get('regionName')}, {resp.get('city')}",
        "Koordinat": f"{resp.get('lat')}, {resp.get('lon')}",
        "Google Maps": f"https://www.google.com/maps?q={resp.get('lat')},{resp.get('lon')}",
        "ISP": resp.get("isp"),
        "Organisasi / ASN": f"{resp.get('org')} ({resp.get('as')})",
        "Proxy / VPN": "Terdeteksi" if resp.get("proxy") else "Tidak",
        "Datacenter / Hosting": "Ya" if resp.get("hosting") else "Tidak",
    }

    table = Table(title="Hasil OSINT IP & Jaringan", border_style=THEME["mauve"])
    table.add_column("Parameter", style=THEME["blue"])
    table.add_column("Informasi", style=THEME["green"])

    for k, v in data.items():
        table.add_row(k, str(v))

    console.print(table)
    saved_path = save_result("ip", ip_addr, data)
    console.print(f"[{THEME['subtext']}]Tersimpan di: {saved_path}[/]")
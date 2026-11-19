import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
from rich.console import Console
from config import THEME, get_saved_api_key, save_json_file, set_saved_api_key

try:
    from googlesearch import search as google_search
except ImportError:
    google_search = None

console = Console()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/129.0.0.0 Safari/537.36"
}


def _normalize_number(raw: str) -> tuple[str, str]:
    """Mengembalikan (nomor_bersih_untuk_api, nomor_tampilan)."""
    digits = "".join(c for c in raw if c.isdigit())
    if raw.startswith("+"):
        return digits, digits
    if digits.startswith("0"):
        # Konversi otomatis format lokal Indonesia (08xx -> 628xx)
        intl_digits = "62" + digits[1:]
        return intl_digits, digits[1:]
    return digits, digits


def _search_google_top5(query_number: str):
    console.print(f"\n[bold {THEME['green']}][FIND][/] [{THEME['yellow']}]Searching Google...[/]")
    results_list = []

    if google_search is not None:
        try:
            raw_results = list(google_search(query_number, num_results=5, advanced=True))
            for idx, item in enumerate(raw_results[:5], start=1):
                if hasattr(item, "url"):
                    results_list.append(
                        {
                            "rank": idx,
                            "title": getattr(item, "title", None) or item.url,
                            "url": item.url,
                            "description": getattr(item, "description", ""),
                        }
                    )
                else:
                    results_list.append({"rank": idx, "title": str(item), "url": str(item)})
        except Exception as e:
            results_list.append({"error": f"Google search rate-limited atau gagal: {e}"})
    else:
        results_list.append({"error": "Library googlesearch-python belum terpasang."})

    save_json_file("Google_Search_Results.json", {"query": query_number, "results": results_list})
    console.print(f"[{THEME['peach']}]Google_Search_Results.json Saved in Data Folder[/]\n")

    console.print(f"[bold {THEME['blue']}][+][/] Top 5 Results for '[bold {THEME['green']}]{query_number}[/]':")
    valid_items = [r for r in results_list if "url" in r]
    if valid_items:
        for r in valid_items:
            console.print(f"[bold {THEME['teal']}]{r['rank']}.[/] {r['title']}")
            console.print(f"   [underline {THEME['blue']}]{r['url']}[/]\n")
    else:
        err_msg = results_list[0].get("error", "Tidak ada hasil ditemukan.") if results_list else "Kosong"
        console.print(f"[{THEME['yellow']}][!] {err_msg}[/]\n")


def _prompt_user_numverify_key() -> str:
    saved_key = get_saved_api_key("numverify")
    if saved_key:
        masked = f"{saved_key[:4]}...{saved_key[-4:]}" if len(saved_key) > 8 else "****"
        choice = console.input(
            f"Enter Your http://numverify.com API KEY (tersimpan: [{THEME['teal']}]{masked}[/], tekan Enter untuk pakai / ketik key baru): "
        ).strip()
        if not choice:
            return saved_key
        set_saved_api_key("numverify", choice)
        return choice

    new_key = console.input(
        "Enter Your http://numverify.com API KEY (atau Enter untuk mode offline):- "
    ).strip()
    if new_key:
        set_saved_api_key("numverify", new_key)
    return new_key


def _validate_phone(raw_number: str, intl_digits: str):
    console.print("=" * 48)
    console.print()
    api_key = _prompt_user_numverify_key()
    console.print(f"[bold {THEME['blue']}][+][/] [{THEME['red']}]Validating phone number...[/]\n")

    validation_payload = {}

    if api_key:
        try:
            url = f"http://apilayer.net/api/validate?access_key={api_key}&number={intl_digits}"
            resp = requests.get(url, timeout=10).json()
            validation_payload = resp
            save_json_file("Phone_Validation.json", validation_payload)
            console.print(f"[{THEME['peach']}]Phone_Validation.json Saved in Data Folder[/]\n")

            if resp.get("valid"):
                console.print(f"[bold {THEME['green']}][+] Valid phone number![/]")
                console.print(f"    Country  : [{THEME['teal']}]{resp.get('country_name')} ({resp.get('country_code')})[/]")
                console.print(f"    Location : [{THEME['teal']}]{resp.get('location') or '-'}[/]")
                console.print(f"    Carrier  : [{THEME['teal']}]{resp.get('carrier') or '-'}[/]")
                console.print(f"    Line Type: [{THEME['teal']}]{resp.get('line_type') or '-'}[/]\n")
                return
            else:
                err_info = resp.get("error", {}).get("info")
                if err_info:
                    console.print(f"[{THEME['red']}][!] Numverify API Error: {err_info}[/]\n")
                else:
                    console.print(f"[{THEME['blue']}][!][/] Invalid phone number.\n")
                return
        except requests.RequestException as e:
            console.print(f"[{THEME['red']}][!] Gagal menghubungi Numverify API ({e}), beralih ke parser lokal...[/]\n")

    # Fallback offline menggunakan library phonenumbers jika pengguna tidak memasukkan API key
    try:
        parsed = phonenumbers.parse(raw_number, "ID")
        is_valid = phonenumbers.is_valid_number(parsed)
        validation_payload = {
            "source": "offline_phonenumbers",
            "valid": is_valid,
            "international_format": phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            ),
            "country": geocoder.description_for_number(parsed, "id") or "Unknown",
            "carrier": carrier.name_for_number(parsed, "id") or "Unknown",
            "timezones": list(timezone.time_zones_for_number(parsed)),
        }
        save_json_file("Phone_Validation.json", validation_payload)
        console.print(f"[{THEME['peach']}]Phone_Validation.json Saved in Data Folder[/]\n")

        if is_valid:
            console.print(f"[bold {THEME['green']}][+] Valid phone number (Offline Mode)[/]")
            console.print(f"    Country  : [{THEME['teal']}]{validation_payload['country']}[/]")
            console.print(f"    Carrier  : [{THEME['teal']}]{validation_payload['carrier']}[/]\n")
        else:
            console.print(f"[{THEME['blue']}][!][/] Invalid phone number.\n")
    except Exception:
        save_json_file("Phone_Validation.json", {"valid": False, "input": raw_number})
        console.print(f"[{THEME['peach']}]Phone_Validation.json Saved in Data Folder[/]\n")
        console.print(f"[{THEME['blue']}][!][/] Invalid phone number.\n")


def _check_social_presence(intl_digits: str, short_digits: str):
    console.print(f"TAKE A LOOK [bold {THEME['blue']}][0_0][/]")
    console.print(
        f"[bold {THEME['blue']}][+][/] Look For Whatsapp : [underline {THEME['blue']}]https://wa.me/{intl_digits}[/]"
    )
    console.print(
        f"[bold {THEME['blue']}][+][/] Look For Telegram : [underline {THEME['blue']}]https://t.me/+{intl_digits}[/]"
    )
    console.print(f"[{THEME['yellow']}]WAIT......[/]")
    console.print("Retrieving Data From Whatsapp\n")

    console.print(f"[bold {THEME['green']}][CHECK][/] Checking Account On Instagram\n")
    console.print(f"[{THEME['red']}]If Status = [FAIL] fail Then Your Account is In Trouble or Account Did Not Exists[/]")
    console.print(f"[{THEME['red']}]If Status = [OK] ok Then Account Exists[/]")

    try:
        ig_url = f"https://www.instagram.com/{short_digits}/"
        resp = requests.get(ig_url, headers=HEADERS, timeout=6)
        if resp.status_code == 200 and "page not found" not in resp.text.lower():
            console.print(f"[bold {THEME['green']}][OK][/] Account Found : [underline {THEME['blue']}]{ig_url}[/]\n")
        else:
            console.print(f"[bold {THEME['blue']}][NOT FOUND][/]   Account Did Not Exists or Unable To Retrieve Data\n")
    except requests.RequestException:
        console.print(f"[bold {THEME['blue']}][NOT FOUND][/]   Account Did Not Exists or Unable To Retrieve Data\n")


def run():
    raw_number = console.input(
        f"[{THEME['mauve']}]Enter Phone Number to search:[/] "
    ).strip()

    if not raw_number:
        console.print(f"[{THEME['red']}]Nomor telepon tidak boleh kosong.[/]")
        return

    intl_digits, short_digits = _normalize_number(raw_number)

    _search_google_top5(short_digits)
    _validate_phone(raw_number, intl_digits)
    _check_social_presence(intl_digits, short_digits)

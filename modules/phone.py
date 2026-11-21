import base64
import json
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from bs4 import BeautifulSoup
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
from rich.console import Console
from config import THEME, get_saved_api_key, save_json_file, set_saved_api_key

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

try:
    from googlesearch import search as google_search
except ImportError:
    google_search = None

console = Console()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}


def _build_number_variants(raw: str) -> dict:
    """Menghasilkan variasi format nomor untuk memperluas jangkauan pencarian."""
    digits = "".join(c for c in raw if c.isdigit())

    if raw.startswith("+"):
        intl_digits = digits
        local_digits = "0" + digits[2:] if digits.startswith("62") else digits
    elif digits.startswith("0"):
        local_digits = digits
        intl_digits = "62" + digits[1:]
    elif digits.startswith("62"):
        intl_digits = digits
        local_digits = "0" + digits[2:]
    else:
        local_digits = digits
        intl_digits = digits

    short_digits = local_digits[1:] if local_digits.startswith("0") else local_digits
    plus_intl = f"+{intl_digits}"

    # Format pemisah umum di iklan/dokumen (contoh: 0822-6979-8833 & 0822 6979 8833)
    if len(local_digits) >= 10:
        dash_fmt = f"{local_digits[:4]}-{local_digits[4:8]}-{local_digits[8:]}"
        space_fmt = f"{local_digits[:4]} {local_digits[4:8]} {local_digits[8:]}"
    else:
        dash_fmt = local_digits
        space_fmt = local_digits

    return {
        "local": local_digits,
        "intl": intl_digits,
        "plus_intl": plus_intl,
        "short": short_digits,
        "dash": dash_fmt,
        "space": space_fmt,
    }


def _decode_bing_url(href: str) -> str:
    """Mendekode URL redirect Bing (u=a1...) menjadi URL tujuan asli."""
    if "bing.com/ck/a" in href:
        try:
            qs = parse_qs(urlparse(href).query)
            u_val = qs.get("u", [""])[0]
            if u_val.startswith("a1"):
                b64 = u_val[2:]
                b64 += "=" * ((4 - len(b64) % 4) % 4)
                decoded = base64.urlsafe_b64decode(b64).decode("utf-8", errors="ignore")
                if decoded.startswith("http"):
                    return decoded
        except Exception:
            pass
    return href


def _decode_ddg_url(href: str) -> str:
    """Mendekode URL redirect DuckDuckGo Lite menjadi URL tujuan asli."""
    if "duckduckgo.com/l/?" in href:
        try:
            qs = parse_qs(urlparse(href).query)
            uddg = qs.get("uddg", [""])[0]
            if uddg.startswith("http"):
                return unquote(uddg)
        except Exception:
            pass
    return href


def _scrape_ddg_lite(query: str, limit: int = 25) -> list[dict]:
    items = []
    try:
        resp = requests.post(
            "https://lite.duckduckgo.com/lite/",
            data={"q": query},
            headers=HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.select("a.result-link"):
                url = _decode_ddg_url(a.get("href", "").strip())
                title = a.get_text(strip=True)
                if url.startswith("http") and "duckduckgo.com" not in url:
                    items.append({"title": title or url, "url": url, "source": "DuckDuckGo-Lite"})
                if len(items) >= limit:
                    break
    except Exception:
        pass
    return items


def _scrape_bing_html(query: str, limit: int = 25) -> list[dict]:
    items = []
    try:
        url = f"https://www.bing.com/search?q={quote_plus(query)}&count={min(limit, 30)}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for li in soup.select("li.b_algo"):
                a = li.find("h2").find("a") if li.find("h2") else None
                if a and a.get("href"):
                    real_url = _decode_bing_url(a["href"].strip())
                    title = a.get_text(strip=True)
                    if real_url.startswith("http") and "bing.com" not in real_url:
                        items.append({"title": title or real_url, "url": real_url, "source": "Bing"})
                if len(items) >= limit:
                    break
    except Exception:
        pass
    return items


def _search_expanded_100(variants: dict, max_results: int = 100) -> list[dict]:
    console.print(
        f"\n[bold {THEME['green']}][FIND][/] [{THEME['yellow']}]Searching across engines & number formats (target up to {max_results} results)...[/]"
    )

    queries = [
        f'"{variants["local"]}"',
        f'"{variants["intl"]}"',
        f'"{variants["plus_intl"]}"',
        f'"{variants["dash"]}"',
        f'"{variants["space"]}"',
        f'"{variants["local"]}" OR "{variants["intl"]}" site:facebook.com OR site:instagram.com OR site:tiktok.com',
        f'"{variants["local"]}" OR "{variants["intl"]}" site:linkedin.com OR site:x.com OR site:twitter.com',
        f'"{variants["local"]}" OR "{variants["intl"]}" site:olx.co.id OR site:tokopedia.com OR site:shopee.co.id',
        f'"{variants["local"]}" OR "{variants["intl"]}" filetype:pdf OR filetype:xlsx OR filetype:docx',
    ]

    seen_urls = set()
    collected = []

    def _add_item(title: str, url: str, source: str):
        if len(collected) >= max_results:
            return
        clean_url = url.strip()
        if not clean_url.startswith("http") or clean_url in seen_urls:
            return
        seen_urls.add(clean_url)
        collected.append(
            {
                "rank": len(collected) + 1,
                "title": title.strip() if title else clean_url,
                "url": clean_url,
                "source": source,
            }
        )

    with console.status(f"[{THEME['yellow']}]Mengumpulkan hingga {max_results} hasil pencarian...[/]"):
        # 1. DuckDuckGo API (ddgs)
        if DDGS is not None:
            for q in queries:
                if len(collected) >= max_results:
                    break
                try:
                    with DDGS() as ddgs:
                        for r in ddgs.text(q, max_results=25):
                            _add_item(r.get("title", ""), r.get("href", ""), "DuckDuckGo")
                            if len(collected) >= max_results:
                                break
                except Exception:
                    continue

        # 2. DuckDuckGo Lite HTML Fallback
        if len(collected) < max_results:
            for q in queries[:5]:
                if len(collected) >= max_results:
                    break
                for item in _scrape_ddg_lite(q, limit=25):
                    _add_item(item["title"], item["url"], item["source"])

        # 3. Bing HTML Fallback (dengan dekoder link asli)
        if len(collected) < max_results:
            for q in queries[:5]:
                if len(collected) >= max_results:
                    break
                for item in _scrape_bing_html(q, limit=25):
                    _add_item(item["title"], item["url"], item["source"])

        # 4. Google Search Fallback
        if len(collected) < max_results and google_search is not None:
            for q in queries[:3]:
                if len(collected) >= max_results:
                    break
                try:
                    for item in google_search(q, num_results=20, advanced=True):
                        if hasattr(item, "url"):
                            _add_item(getattr(item, "title", "") or item.url, item.url, "Google")
                        else:
                            _add_item(str(item), str(item), "Google")
                except Exception:
                    continue

    # Sertakan juga tautan OSINT Dork yang selalu aktif dan bisa diklik
    base_query = f'"{variants["local"]}" OR "{variants["intl"]}"'
    social_query = f'({base_query}) (site:facebook.com OR site:instagram.com OR site:tiktok.com OR site:linkedin.com)'
    doc_query = f'({base_query}) (filetype:pdf OR filetype:xlsx OR filetype:csv OR site:pastebin.com)'

    direct_dorks = {
        "Google Exact Match": f"https://www.google.com/search?q={quote_plus(base_query)}",
        "DuckDuckGo Exact Match": f"https://duckduckgo.com/?q={quote_plus(base_query)}",
        "Bing Exact Match": f"https://www.bing.com/search?q={quote_plus(base_query)}",
        "Social Media Dork": f"https://www.google.com/search?q={quote_plus(social_query)}",
        "Document & Leak Dork": f"https://www.google.com/search?q={quote_plus(doc_query)}",
        "Truecaller Web Lookup": f"https://www.truecaller.com/search/id/{variants['short']}",
        "Sync.me Web Lookup": f"https://sync.me/search/?number={variants['intl']}",
    }

    save_json_file(
        "Google_Search_Results.json",
        {
            "variants": variants,
            "total_found": len(collected),
            "results": collected,
            "direct_osint_links": direct_dorks,
        },
    )
    console.print(f"[{THEME['peach']}]Google_Search_Results.json Saved in Data Folder ({len(collected)} results)[/]\n")

    console.print(
        f"[bold {THEME['blue']}][+][/] Found [bold {THEME['green']}]{len(collected)}[/] Results for '[bold {THEME['green']}]{variants['local']}[/]' / '[bold {THEME['green']}]{variants['intl']}[/]':"
    )
    if collected:
        for r in collected:
            console.print(
                f"[bold {THEME['teal']}]{r['rank']}.[/] {r['title']} [{THEME['subtext']}][{r['source']}][/]"
            )
            console.print(f"   [underline {THEME['blue']}]{r['url']}[/]")
        console.print()
    else:
        console.print(
            f"[{THEME['yellow']}][!] Mesin pencari membatasi scraping otomatis saat ini. Gunakan Direct OSINT Links di bawah:[/]\n"
        )

    console.print(f"[bold {THEME['mauve']}][+] Direct Clickable OSINT Search Links (Valid & Ready):[/]")
    for label, link in direct_dorks.items():
        console.print(f"   • {label:<23}: [underline {THEME['blue']}]{link}[/]")
    console.print()

    return collected


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

    if api_key:
        try:
            url = f"http://apilayer.net/api/validate?access_key={api_key}&number={intl_digits}"
            resp = requests.get(url, timeout=10).json()
            save_json_file("Phone_Validation.json", resp)
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

    # Fallback offline menggunakan library phonenumbers
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


def _check_social_presence(variants: dict):
    intl_digits = variants["intl"]
    local_digits = variants["local"]

    console.print(f"TAKE A LOOK [bold {THEME['blue']}][0_0][/]")
    console.print(
        f"[bold {THEME['blue']}][+][/] Look For Whatsapp (Direct) : [underline {THEME['blue']}]https://wa.me/{intl_digits}[/]"
    )
    console.print(
        f"[bold {THEME['blue']}][+][/] Look For Whatsapp (API)    : [underline {THEME['blue']}]https://api.whatsapp.com/send?phone={intl_digits}[/]"
    )
    console.print(
        f"[bold {THEME['blue']}][+][/] Look For Telegram          : [underline {THEME['blue']}]https://t.me/+{intl_digits}[/]"
    )
    console.print(f"[{THEME['yellow']}]WAIT......[/]")
    console.print("Checking Instagram Account Recovery Status...\n")

    console.print(f"[bold {THEME['green']}][CHECK][/] Checking Account On Instagram\n")

    ig_query = f'site:instagram.com ("{local_digits}" OR "{intl_digits}")'
    ig_dork = f"https://www.google.com/search?q={quote_plus(ig_query)}"

    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        session.get("https://www.instagram.com/accounts/password/reset/", timeout=8)
        csrf_token = session.cookies.get("csrftoken", "")

        ajax_headers = {
            **HEADERS,
            "X-CSRFToken": csrf_token,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/password/reset/",
        }
        resp = session.post(
            "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/",
            data={"email_or_username": f"+{intl_digits}"},
            headers=ajax_headers,
            timeout=8,
        )
        data = resp.json()
        if data.get("status") == "ok":
            console.print(f"[bold {THEME['green']}][OK][/] Nomor terdaftar di Instagram (Recovery Endpoint Terkonfirmasi)!")
            console.print(f"     Cari Profil Terkait : [underline {THEME['blue']}]{ig_dork}[/]\n")
        else:
            console.print(f"[bold {THEME['blue']}][NOT FOUND][/] Tidak terdeteksi via recovery langsung.")
            console.print(f"     Cek Indeks Google   : [underline {THEME['blue']}]{ig_dork}[/]\n")
    except (json.JSONDecodeError, requests.RequestException):
        console.print(f"[bold {THEME['yellow']}][INFO][/] Instagram membatasi pengecekan otomatis.")
        console.print(f"     Cek Indeks Google   : [underline {THEME['blue']}]{ig_dork}[/]\n")


def run():
    raw_number = console.input(
        f"[{THEME['mauve']}]Enter Phone Number to search:[/] "
    ).strip()

    if not raw_number:
        console.print(f"[{THEME['red']}]Nomor telepon tidak boleh kosong.[/]\n")
        return

    limit_input = console.input(
        f"[{THEME['teal']}]Max search results (1-100, default 100):[/] "
    ).strip()
    max_results = min(max(int(limit_input), 1), 100) if limit_input.isdigit() else 100

    variants = _build_number_variants(raw_number)

    _search_expanded_100(variants, max_results=max_results)
    _validate_phone(raw_number, variants["intl"])
    _check_social_presence(variants)

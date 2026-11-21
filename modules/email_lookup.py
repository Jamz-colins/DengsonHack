from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import re
import time
from urllib.parse import quote, quote_plus
import dns.resolver
import requests
from rich.console import Console
from config import THEME, save_json_file

try:
    from googlesearch import search as google_search
except ImportError:
    google_search = None

console = Console()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}


def _google_email_dork(email: str, domain_filter: str = "") -> str:
    query = f'"{email}" {domain_filter}'.strip()
    return f"https://www.google.com/search?q={quote_plus(query)}"


# ==============================================================================
# DAFTAR PENGECEKAN PLATFORM (MENGEMBALIKAN URL PUBLIK YANG VALID)
# ==============================================================================

def _check_adobe(email: str) -> tuple[bool, str]:
    url = "https://auth.services.adobe.com/signin/v2/users/accounts"
    headers = {**HEADERS, "Content-Type": "application/json", "X-IMS-ClientId": "SunbreakWebUI1"}
    try:
        r = requests.post(url, json={"username": email}, headers=headers, timeout=7)
        if r.status_code == 200 and isinstance(r.json(), list) and len(r.json()) > 0:
            return True, _google_email_dork(email, "site:adobe.com OR site:behance.net")
    except Exception:
        pass
    return False, ""


def _check_spotify(email: str) -> tuple[bool, str]:
    url = f"https://spclient.wg.spotify.com/signup/public/v1/account?validate=1&email={quote(email)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200 and r.json().get("status") == 20:
            return True, _google_email_dork(email, "site:open.spotify.com")
    except Exception:
        pass
    return False, ""


def _check_twitter(email: str) -> tuple[bool, str]:
    url = f"https://api.twitter.com/i/users/email_available.json?email={quote(email)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200 and r.json().get("taken") is True:
            return True, _google_email_dork(email, "site:x.com OR site:twitter.com")
    except Exception:
        pass
    return False, ""


def _check_github(email: str) -> tuple[bool, str]:
    api_url = f"https://api.github.com/search/users?q={quote(email)}+in:email"
    try:
        r = requests.get(api_url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            items = r.json().get("items", [])
            if items and items[0].get("html_url"):
                return True, items[0]["html_url"]
    except Exception:
        pass
    return False, ""


def _check_duolingo(email: str) -> tuple[bool, str]:
    api_url = f"https://www.duolingo.com/2017-06-30/users?email={quote(email)}"
    try:
        r = requests.get(api_url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            users = r.json().get("users", [])
            if users:
                uname = users[0].get("username")
                if uname:
                    return True, f"https://www.duolingo.com/profile/{uname}"
                return True, _google_email_dork(email, "site:duolingo.com")
    except Exception:
        pass
    return False, ""


def _check_gravatar(email: str) -> tuple[bool, str]:
    email_hash = hashlib.md5(email.encode("utf-8")).hexdigest()
    json_url = f"https://en.gravatar.com/{email_hash}.json"
    profile_url = f"https://gravatar.com/{email_hash}"
    try:
        r = requests.get(json_url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            entry = r.json().get("entry", [{}])[0]
            return True, entry.get("profileUrl", profile_url)
    except Exception:
        pass
    return False, ""


def _check_proton(email: str) -> tuple[bool, str]:
    url = f"https://api.protonmail.ch/pks/lookup?op=index&search={quote(email)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200 and "info:1:1" in r.text:
            return True, f"https://api.protonmail.ch/pks/lookup?op=get&search={quote(email)}"
    except Exception:
        pass
    return False, ""


def _check_wordpress(email: str) -> tuple[bool, str]:
    url = f"https://public-api.wordpress.com/rest/v1.1/users/{quote(email)}/auth-options"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200 and "email_verified" in r.text:
            return True, _google_email_dork(email, "site:wordpress.com")
    except Exception:
        pass
    return False, ""


def _check_imgur(email: str) -> tuple[bool, str]:
    url = "https://imgur.com/signin/ajax_email_available"
    try:
        r = requests.post(url, data={"email": email}, headers=HEADERS, timeout=7)
        if r.status_code == 200 and r.json().get("data", {}).get("available") is False:
            return True, _google_email_dork(email, "site:imgur.com")
    except Exception:
        pass
    return False, ""


def _check_pinterest(email: str) -> tuple[bool, str]:
    encoded_data = quote(f'{{"options":{{"email":"{email}"}}}}')
    url = f"https://www.pinterest.com/_ngjs/resource/EmailExistsResource/get/?data={encoded_data}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200 and r.json().get("resource_response", {}).get("data") is True:
            return True, _google_email_dork(email, "site:pinterest.com")
    except Exception:
        pass
    return False, ""


def _check_gitlab(email: str) -> tuple[bool, str]:
    url = f"https://gitlab.com/users/{quote(email)}/exists"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200 and r.json().get("exists") is True:
            return True, _google_email_dork(email, "site:gitlab.com")
    except Exception:
        pass
    return False, ""


def _check_bitbucket(email: str) -> tuple[bool, str]:
    url = f"https://bitbucket.org/account/check-email/?email={quote(email)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200 and r.json().get("exists") is True:
            return True, _google_email_dork(email, "site:bitbucket.org")
    except Exception:
        pass
    return False, ""


def _check_dockerhub(email: str) -> tuple[bool, str]:
    url = "https://hub.docker.com/v2/users/signup/"
    try:
        r = requests.post(url, json={"email": email, "username": "", "password": ""}, headers=HEADERS, timeout=7)
        if "already exists" in r.text.lower() or "already in use" in r.text.lower():
            return True, _google_email_dork(email, "site:hub.docker.com")
    except Exception:
        pass
    return False, ""


def _check_chesscom(email: str) -> tuple[bool, str]:
    url = f"https://www.chess.com/callback/email/available?email={quote(email)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200 and r.json().get("isEmailAvailable") is False:
            return True, _google_email_dork(email, "site:chess.com")
    except Exception:
        pass
    return False, ""


def _check_strava(email: str) -> tuple[bool, str]:
    url = f"https://www.strava.com/athletes/email_unique?email={quote(email)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200 and r.text.strip().lower() == "false":
            return True, _google_email_dork(email, "site:strava.com")
    except Exception:
        pass
    return False, ""


def _check_lastfm(email: str) -> tuple[bool, str]:
    url = "https://www.last.fm/join/partial/validate"
    try:
        r = requests.post(url, data={"field": "email", "value": email}, headers=HEADERS, timeout=7)
        if r.status_code == 200 and ("already" in r.text.lower() or "in use" in r.text.lower()):
            return True, _google_email_dork(email, "site:last.fm")
    except Exception:
        pass
    return False, ""


def _check_archive(email: str) -> tuple[bool, str]:
    url = "https://archive.org/account/signup"
    try:
        r = requests.post(url, data={"input_name": "email", "input_value": email}, headers=HEADERS, timeout=7)
        if r.status_code == 200 and "already taken" in r.text.lower():
            return True, _google_email_dork(email, "site:archive.org")
    except Exception:
        pass
    return False, ""


def _check_wattpad(email: str) -> tuple[bool, str]:
    url = f"https://www.wattpad.com/api/v3/users/validate?email={quote(email)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code in (200, 400) and ("already" in r.text.lower() or "taken" in r.text.lower()):
            return True, _google_email_dork(email, "site:wattpad.com")
    except Exception:
        pass
    return False, ""


def _check_vimeo(email: str) -> tuple[bool, str]:
    url = f"https://vimeo.com/join/check_email?email={quote(email)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200 and ("already" in r.text.lower() or "taken" in r.text.lower()):
            return True, _google_email_dork(email, "site:vimeo.com")
    except Exception:
        pass
    return False, ""


def _check_flickr(email: str) -> tuple[bool, str]:
    url = f"https://identity.flickr.com/check-email?email={quote(email)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200 and r.json().get("exists") is True:
            return True, _google_email_dork(email, "site:flickr.com")
    except Exception:
        pass
    return False, ""


def _check_eventbrite(email: str) -> tuple[bool, str]:
    url = "https://www.eventbrite.com/api/v3/users/lookup/"
    try:
        r = requests.post(url, json={"email": email}, headers=HEADERS, timeout=7)
        if r.status_code == 200 and r.json().get("exists") is True:
            return True, _google_email_dork(email, "site:eventbrite.com")
    except Exception:
        pass
    return False, ""


def _check_codecademy(email: str) -> tuple[bool, str]:
    url = "https://www.codecademy.com/users/validate"
    try:
        r = requests.post(url, json={"user": {"email": email}}, headers=HEADERS, timeout=7)
        if "already been taken" in r.text.lower():
            return True, _google_email_dork(email, "site:codecademy.com")
    except Exception:
        pass
    return False, ""


def _check_zoho(email: str) -> tuple[bool, str]:
    url = "https://accounts.zoho.com/register/field/validate"
    try:
        r = requests.post(url, data={"email": email}, headers=HEADERS, timeout=7)
        if "already exists" in r.text.lower() or "already registered" in r.text.lower():
            return True, _google_email_dork(email, "site:zoho.com")
    except Exception:
        pass
    return False, ""


def _check_mailru(email: str) -> tuple[bool, str]:
    url = f"https://account.mail.ru/api/v1/user/exists?email={quote(email)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200 and r.json().get("body", {}).get("exists") is True:
            return True, _google_email_dork(email, "site:mail.ru")
    except Exception:
        pass
    return False, ""


def _check_rambler(email: str) -> tuple[bool, str]:
    url = "https://id.rambler.ru/jsonrpc"
    payload = {
        "method": "Rambler::Id::login_available",
        "params": [{"login": email}],
        "rpc": "2.0",
    }
    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=7)
        if r.status_code == 200 and r.json().get("result", {}).get("available") == 0:
            return True, _google_email_dork(email, "site:rambler.ru")
    except Exception:
        pass
    return False, ""


SERVICE_CHECKS = {
    "Adobe": _check_adobe,
    "Spotify": _check_spotify,
    "Twitter / X": _check_twitter,
    "GitHub": _check_github,
    "Duolingo": _check_duolingo,
    "Gravatar": _check_gravatar,
    "ProtonMail": _check_proton,
    "WordPress": _check_wordpress,
    "Imgur": _check_imgur,
    "Pinterest": _check_pinterest,
    "GitLab": _check_gitlab,
    "Bitbucket": _check_bitbucket,
    "DockerHub": _check_dockerhub,
    "Chess.com": _check_chesscom,
    "Strava": _check_strava,
    "Last.fm": _check_lastfm,
    "Archive.org": _check_archive,
    "Wattpad": _check_wattpad,
    "Vimeo": _check_vimeo,
    "Flickr": _check_flickr,
    "Eventbrite": _check_eventbrite,
    "Codecademy": _check_codecademy,
    "Zoho": _check_zoho,
    "Mail.ru": _check_mailru,
    "Rambler": _check_rambler,
}


# ==============================================================================
# PENGECEKAN LANJUTAN (FIREFOX, BREACH DATA, PASTEBIN, INSTAGRAM)
# ==============================================================================

def _check_firefox(email: str) -> bool:
    console.print(f"[{THEME['yellow']}]Checking On Firefox....[/]")
    console.print(f"[bold {THEME['green']}][CHECK][/] Checking On Firefox", end="")
    for _ in range(10):
        time.sleep(0.05)
        console.print(f"[{THEME['yellow']}].[/]", end="")
    console.print()

    try:
        resp = requests.post(
            "https://api.accounts.firefox.com/v1/account/status",
            json={"email": email},
            headers=HEADERS,
            timeout=8,
        )
        if resp.status_code == 200 and resp.json().get("exists") is True:
            console.print(f"[bold {THEME['green']}][+][/] Firefox: Registered\n")
            return True
    except Exception:
        pass

    console.print(f"[bold {THEME['blue']}][-][/] Firefox: Not registered\n")
    return False


def _check_breach_data(email: str) -> dict:
    console.print(f"[{THEME['yellow']}]Checking On Breach Data....[/]")
    api_url = f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-email?email={quote(email)}"
    try:
        resp = requests.get(api_url, headers=HEADERS, timeout=10)
        raw_text = resp.text.strip()
        try:
            parsed_json = resp.json()
            compact_json = json.dumps(parsed_json, separators=(",", ":"))
            console.print(f"[{THEME['green']}]{compact_json}[/]")
            console.print(
                f"[bold {THEME['blue']}][+][/] Cek Detail Kebocoran : [underline {THEME['blue']}]https://www.hudsonrock.com/free-tools[/]\n"
            )
            return parsed_json
        except json.JSONDecodeError:
            console.print(f"[{THEME['subtext']}]{raw_text}[/]\n")
            return {"raw": raw_text}
    except requests.RequestException as e:
        err = {"error": f"Failed to fetch breach data: {e}"}
        console.print(f"[{THEME['red']}]{json.dumps(err)}[/]\n")
        return err


def _check_pastebin(email: str) -> list[str]:
    console.print(f"[{THEME['yellow']}]Checking On PASTEBIN....[/]")
    found_links = []

    if google_search is not None:
        try:
            results = list(google_search(f'site:pastebin.com "{email}"', num_results=5))
            found_links = [str(link) for link in results if "pastebin.com" in str(link)]
        except Exception:
            found_links = []

    if found_links:
        for link in found_links:
            console.print(f"[bold {THEME['green']}][+][/] Paste Found: [underline {THEME['blue']}]{link}[/]")
        console.print()
    else:
        pb_dork = _google_email_dork(email, "site:pastebin.com")
        console.print(f"[bold {THEME['blue']}][INFO][/] No paste found automatically.")
        console.print(f"[bold {THEME['blue']}][+][/] Manual Pastebin Dork : [underline {THEME['blue']}]{pb_dork}[/]\n")

    return found_links


def _check_instagram(email: str) -> dict:
    console.print(f"[{THEME['yellow']}]Checking On Instagram....[/]")
    ig_dork = _google_email_dork(email, "site:instagram.com")
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
            data={"email_or_username": email},
            headers=ajax_headers,
            timeout=8,
        )
        data = resp.json()
        if data.get("status") == "ok":
            console.print(f"[bold {THEME['green']}][+][/] Instagram: Registered")
            console.print(f"[bold {THEME['blue']}][+][/] Search Profile: [underline {THEME['blue']}]{ig_dork}[/]\n")
            return {"registered": True, "response": data}
        console.print(f"[bold {THEME['blue']}][-][/] Instagram: {data.get('message', 'Not registered')}\n")
        return {"registered": False, "response": data}
    except (json.JSONDecodeError, requests.RequestException):
        console.print(f"[bold {THEME['yellow']}][INFO][/] Instagram membatasi akses otomatis.")
        console.print(f"[bold {THEME['blue']}][+][/] Search Profile: [underline {THEME['blue']}]{ig_dork}[/]\n")
        return {"error": "Rate limited by Instagram"}


# ==============================================================================
# ENTRY POINT MODUL EMAIL
# ==============================================================================

def run():
    email = console.input(
        f"[{THEME['mauve']}]Enter Email to search:[/] "
    ).strip().lower()

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        console.print(f"[{THEME['red']}]Format email tidak valid.[/]\n")
        return

    console.print(f"\n[bold {THEME['blue']}]Checking Email: {email}[/]")
    console.print(f"[bold {THEME['green']}]Only Registered Data & Valid Public Links Will Be Provided...[/]\n")

    registered_services = {}

    with console.status(f"[{THEME['yellow']}]Scanning {len(SERVICE_CHECKS)} platforms concurrently...[/]"):
        with ThreadPoolExecutor(max_workers=15) as executor:
            future_map = {
                executor.submit(func, email): label
                for label, func in SERVICE_CHECKS.items()
            }
            for future in as_completed(future_map):
                label = future_map[future]
                try:
                    is_registered, public_url = future.result()
                    if is_registered:
                        registered_services[label] = public_url
                        console.print(
                            f"[bold {THEME['red']}][+][/] {label:<13}: Registered -> [underline {THEME['blue']}]{public_url}[/]"
                        )
                except Exception:
                    pass

    if not registered_services:
        console.print(
            f"[{THEME['subtext']}][INFO] No registered public accounts matched across {len(SERVICE_CHECKS)} platforms.[/]"
        )

    global_dork = _google_email_dork(email)
    console.print(f"[bold {THEME['blue']}][+][/] Global Web Search : [underline {THEME['blue']}]{global_dork}[/]")

    domain = email.split("@")[1]
    try:
        mx_records = [str(r.exchange).rstrip(".") for r in dns.resolver.resolve(domain, "MX")]
    except Exception:
        mx_records = []

    report_payload = {
        "email": email,
        "domain": domain,
        "mx_records": mx_records,
        "md5_hash": hashlib.md5(email.encode("utf-8")).hexdigest(),
        "total_platforms_scanned": len(SERVICE_CHECKS),
        "registered_services": registered_services,
        "global_search_url": global_dork,
    }
    save_json_file("email_information.json", report_payload)
    console.print(f"[bold {THEME['green']}][+] Results saved to Data/email_information.json[/]\n")

    firefox_status = _check_firefox(email)
    breach_data = _check_breach_data(email)
    pastebin_links = _check_pastebin(email)
    instagram_status = _check_instagram(email)

    report_payload.update(
        {
            "firefox_registered": firefox_status,
            "breach_data": breach_data,
            "pastebin_results": pastebin_links,
            "instagram": instagram_status,
        }
    )
    save_json_file("email_information.json", report_payload)

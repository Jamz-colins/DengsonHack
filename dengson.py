#!/usr/bin/env python3
import getpass
import os
import socket
import sys
import pyfiglet
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from config import APP_NAME, AUTHOR, GITHUB, THEME, VERSION
from modules import email_lookup, ip_lookup, phone, username, yt_comments

console = Console()


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def get_device_owner() -> str:
    try:
        user = getpass.getuser()
    except Exception:
        user = os.environ.get("USER") or os.environ.get("USERNAME") or "Owner"
    hostname = socket.gethostname()
    return f"{user}@{hostname}"


def show_exit_greeting():
    owner = get_device_owner()
    console.print()
    console.print(
        Panel(
            f"[bold {THEME['teal']}]Halo & sampai jumpa, [bold {THEME['mauve']}]{owner}[/]![/]\n"
            f"[{THEME['subtext']}]Terima kasih telah menggunakan {APP_NAME} v{VERSION}.[/]",
            box=box.ROUNDED,
            border_style=THEME["mauve"],
            expand=False,
            padding=(0, 2),
        )
    )


def show_banner():
    clear_screen()
    ascii_art = pyfiglet.figlet_format(APP_NAME, font="slant")
    console.print(Text(ascii_art, style=f"bold {THEME['mauve']}"))

    info_text = (
        f"[bold {THEME['teal']}]Welcome to {APP_NAME}[/]\n"
        f"[{THEME['blue']}]Created By :[/] [{THEME['mauve']}]{AUTHOR}[/]\n"
        f"[{THEME['blue']}]GitHub     :[/] [{THEME['mauve']}]{GITHUB}[/]\n"
        f"[{THEME['blue']}]Version    :[/] [{THEME['green']}]{VERSION}[/]"
    )
    console.print(
        Panel(
            info_text,
            box=box.DOUBLE,
            border_style=THEME["teal"],
            expand=False,
            padding=(0, 2),
        )
    )
    console.print(
        f"\n[bold {THEME['green']}]{APP_NAME} - Terminal-Based OSINT Toolkit[/]"
    )
    console.print(
        f"[bold {THEME['yellow']}]Gather intelligence from numbers, usernames, IPs & more - all in one place![/]"
    )


def show_menu():
    options = [
        ("1", "Information By Number"),
        ("2", "Information By Username"),
        ("3", "Information By Email"),
        ("4", "Information By IP"),
        ("5", "Fetch YouTube Comments"),
        ("6", "Exit"),
    ]
    console.print(f"[{THEME['subtext']}]Please select an option:[/]")
    for num, label in options:
        color = THEME["red"] if num == "6" else THEME["green"]
        console.print(f"[bold {THEME['teal']}]{num}.[/] [{color}]{label}[/]")


def main():
    actions = {
        "1": phone.run,
        "2": username.run,
        "3": email_lookup.run,
        "4": ip_lookup.run,
        "5": yt_comments.run,
    }

    show_banner()
    while True:
        show_menu()
        choice = console.input(f"[bold {THEME['green']}]Enter Your Choice: [/]").strip()

        if choice == "6":
            show_exit_greeting()
            sys.exit(0)

        action = actions.get(choice)
        if action:
            action()
        else:
            console.print(f"[{THEME['red']}]Pilihan tidak valid![/]\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print()
        show_exit_greeting()
        sys.exit(0)

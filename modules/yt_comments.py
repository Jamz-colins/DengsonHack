from itertools import islice
from rich.console import Console
from rich.table import Table
from youtube_comment_downloader import SORT_BY_RECENT, YoutubeCommentDownloader
from config import THEME, save_result

console = Console()


def run():
    url = console.input(
        f"[{THEME['teal']}]Masukkan URL Video YouTube: [/]"
    ).strip()
    limit_str = console.input(
        f"[{THEME['teal']}]Jumlah komentar yang diambil (default 15): [/]"
    ).strip()
    limit = int(limit_str) if limit_str.isdigit() else 15

    downloader = YoutubeCommentDownloader()
    comments_data = []

    with console.status(f"[{THEME['yellow']}]Mengambil komentar terbaru dari YouTube...[/]"):
        try:
            generator = downloader.get_comments_from_url(url, sort_by=SORT_BY_RECENT)
            for item in islice(generator, limit):
                comments_data.append(
                    {
                        "author": item.get("author", "-"),
                        "time": item.get("time", "-"),
                        "votes": item.get("votes", "0"),
                        "text": item.get("text", "").replace("\n", " "),
                    }
                )
        except Exception as e:
            console.print(f"[{THEME['red']}]Gagal mengambil komentar: {e}[/]")
            return

    if not comments_data:
        console.print(f"[{THEME['yellow']}]Komentar tidak ditemukan atau dinonaktifkan.[/]")
        return

    table = Table(title=f"{len(comments_data)} Komentar Terbaru", border_style=THEME["mauve"])
    table.add_column("Akun", style=THEME["blue"], max_width=22)
    table.add_column("Waktu", style=THEME["yellow"], max_width=15)
    table.add_column("Komentar", style=THEME["green"])

    for c in comments_data:
        table.add_row(c["author"], c["time"], c["text"][:100])

    console.print(table)
    saved_path = save_result("youtube_comments", url, {"total": len(comments_data), "comments": comments_data})
    console.print(f"[{THEME['subtext']}]Tersimpan di: {saved_path}[/]")
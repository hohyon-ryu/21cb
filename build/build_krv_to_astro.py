#!/usr/bin/env python3
"""개역한글(1961) JSON → astro/src/content/krv-<slug>/<chapter>.md

데이터 출처: https://github.com/bluesaurel/Korean-Bible-1961-KRV (Public Domain)
저작자 표시: 대한성서공회.

사용법:
  python3 build_krv_to_astro.py [<source-dir>]

기본 source: /tmp/Korean-Bible-1961-KRV/data
"""
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DST = ROOT / "astro/src/content"
DEFAULT_SRC = pathlib.Path("/tmp/Korean-Bible-1961-KRV/data")

# 기존 성인 본문 이모지 매핑 재활용
spec = importlib.util.spec_from_file_location("bw", ROOT / "build/build_web.py")
bw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bw)
ADULT_EMOJI = bw.CHAPTER_EMOJI_BY_BOOK

# KRV 영문 책명 → (한글책명, astro slug) 매핑
BOOKS = {
    "Genesis": ("창세기", "genesis"),
    "Exodus": ("출애굽기", "exodus"),
    "Leviticus": ("레위기", "leviticus"),
    "Numbers": ("민수기", "numbers"),
    "Deuteronomy": ("신명기", "deuteronomy"),
    "Joshua": ("여호수아", "joshua"),
    "Judges": ("사사기", "judges"),
    "Ruth": ("룻기", "ruth"),
    "1Samuel": ("사무엘상", "samuel1"),
    "2Samuel": ("사무엘하", "samuel2"),
    "1Kings": ("열왕기상", "kings1"),
    "2Kings": ("열왕기하", "kings2"),
    "1Chronicles": ("역대상", "chronicles1"),
    "2Chronicles": ("역대하", "chronicles2"),
    "Ezra": ("에스라", "ezra"),
    "Nehemiah": ("느헤미야", "nehemiah"),
    "Esther": ("에스더", "esther"),
    "Job": ("욥기", "job"),
    "Psalms": ("시편", "psalms"),
    "Proverbs": ("잠언", "proverbs"),
    "Ecclesiastes": ("전도서", "ecclesiastes"),
    "SongofSolomon": ("아가", "song"),
    "Isaiah": ("이사야", "isaiah"),
    "Jeremiah": ("예레미야", "jeremiah"),
    "Lamentations": ("예레미야애가", "lamentations"),
    "Ezekiel": ("에스겔", "ezekiel"),
    "Daniel": ("다니엘", "daniel"),
    "Hosea": ("호세아", "hosea"),
    "Joel": ("요엘", "joel"),
    "Amos": ("아모스", "amos"),
    "Obadiah": ("오바댜", "obadiah"),
    "Jonah": ("요나", "jonah"),
    "Micah": ("미가", "micah"),
    "Nahum": ("나훔", "nahum"),
    "Habakkuk": ("하박국", "habakkuk"),
    "Zephaniah": ("스바냐", "zephaniah"),
    "Haggai": ("학개", "haggai"),
    "Zechariah": ("스가랴", "zechariah"),
    "Malachi": ("말라기", "malachi"),
    "Matthew": ("마태복음", "matthew"),
    "Mark": ("마가복음", "mark"),
    "Luke": ("누가복음", "luke"),
    "John": ("요한복음", "john"),
    "Acts": ("사도행전", "acts"),
    "Romans": ("로마서", "romans"),
    "1Corinthians": ("고린도전서", "corinthians1"),
    "2Corinthians": ("고린도후서", "corinthians2"),
    "Galatians": ("갈라디아서", "galatians"),
    "Ephesians": ("에베소서", "ephesians"),
    "Philippians": ("빌립보서", "philippians"),
    "Colossians": ("골로새서", "colossians"),
    "1Thessalonians": ("데살로니가전서", "thessalonians1"),
    "2Thessalonians": ("데살로니가후서", "thessalonians2"),
    "1Timothy": ("디모데전서", "timothy1"),
    "2Timothy": ("디모데후서", "timothy2"),
    "Titus": ("디도서", "titus"),
    "Philemon": ("빌레몬서", "philemon"),
    "Hebrews": ("히브리서", "hebrews"),
    "James": ("야고보서", "james"),
    "1Peter": ("베드로전서", "peter1"),
    "2Peter": ("베드로후서", "peter2"),
    "1John": ("요한일서", "john1"),
    "2John": ("요한이서", "john2"),
    "3John": ("요한삼서", "john3"),
    "Jude": ("유다서", "jude"),
    "Revelation": ("요한계시록", "revelation"),
}


def emoji_for(book_ko: str, chap: int) -> str:
    return ADULT_EMOJI.get(book_ko, {}).get(chap, "📖")


def chapter_label(book_ko: str, chap: int) -> str:
    # 시편만 "편", 나머지는 "장"
    return f"{chap}편" if book_ko == "시편" else f"{chap}장"


def build_chapter_md(book_ko: str, chap: int, verses: list[dict]) -> str:
    emoji = emoji_for(book_ko, chap)
    label = chapter_label(book_ko, chap)
    title = f"{book_ko} {label}"
    lines = [
        "---",
        f"chapter: {chap}",
        f'title: "개역한글"',
        f'emoji: "{emoji}"',
        "---",
        "",
    ]
    for v in verses:
        n = v["verse"]
        text = v["text"].strip()
        lines.append(f'<sup class="verse">{n}</sup> {text}')
        lines.append("")
    return "\n".join(lines)


def build_book(src_dir: pathlib.Path, krv_name: str, book_ko: str, slug: str) -> int:
    src_file = src_dir / f"{krv_name}.json"
    if not src_file.exists():
        print(f"  ! missing {src_file}")
        return 0
    with src_file.open(encoding="utf-8") as f:
        data = json.load(f)
    out_dir = DST / f"krv-{slug}"
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for ch in data["chapters"]:
        chap = ch["chapter"]
        verses = ch["verses"]
        content = build_chapter_md(book_ko, chap, verses)
        (out_dir / f"{chap:02d}.md").write_text(content, encoding="utf-8")
        count += 1
    return count


def main() -> None:
    src_dir = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src_dir.exists():
        print(f"source not found: {src_dir}")
        sys.exit(1)
    total = 0
    for krv_name, (book_ko, slug) in BOOKS.items():
        n = build_book(src_dir, krv_name, book_ko, slug)
        if n > 0:
            print(f"{book_ko} → krv-{slug}: {n}")
            total += n
    print(f"\n총 {total}장")


if __name__ == "__main__":
    main()

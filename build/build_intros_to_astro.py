#!/usr/bin/env python3
"""책 소개(intro.md) → astro/src/content/intros/<slug>.md 동기화.

각 책 root 디렉토리의 intro.md를 가져와 frontmatter 추가 후 astro intros 컬렉션에 배치.

Source format (`<책>/intro.md`):
  ---
  author: "..."         # optional
  era: "..."            # optional
  themes:               # optional
    - "..."
  summary: "한 줄 요약" # optional
  ---
  본문 마크다운 (단락, ###, > quote 등 자유)
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DST = ROOT / "astro/src/content/intros"

BOOKS = [
    ("창세기", "genesis"), ("출애굽기", "exodus"), ("레위기", "leviticus"),
    ("민수기", "numbers"), ("신명기", "deuteronomy"), ("여호수아", "joshua"),
    ("사사기", "judges"), ("룻기", "ruth"), ("사무엘상", "samuel1"),
    ("사무엘하", "samuel2"), ("열왕기상", "kings1"), ("열왕기하", "kings2"),
    ("역대상", "chronicles1"), ("역대하", "chronicles2"), ("에스라", "ezra"),
    ("느헤미야", "nehemiah"), ("에스더", "esther"), ("욥기", "job"),
    ("시편", "psalms"), ("잠언", "proverbs"), ("전도서", "ecclesiastes"),
    ("아가", "song"), ("이사야", "isaiah"), ("예레미야", "jeremiah"),
    ("예레미야애가", "lamentations"), ("에스겔", "ezekiel"), ("다니엘", "daniel"),
    ("호세아", "hosea"), ("요엘", "joel"), ("아모스", "amos"),
    ("오바댜", "obadiah"), ("요나", "jonah"), ("미가", "micah"),
    ("나훔", "nahum"), ("하박국", "habakkuk"), ("스바냐", "zephaniah"),
    ("학개", "haggai"), ("스가랴", "zechariah"), ("말라기", "malachi"),
    ("마태복음", "matthew"), ("마가복음", "mark"), ("누가복음", "luke"),
    ("요한복음", "john"), ("사도행전", "acts"), ("로마서", "romans"),
    ("고린도전서", "corinthians1"), ("고린도후서", "corinthians2"),
    ("갈라디아서", "galatians"), ("에베소서", "ephesians"),
    ("빌립보서", "philippians"), ("골로새서", "colossians"),
    ("데살로니가전서", "thessalonians1"), ("데살로니가후서", "thessalonians2"),
    ("디모데전서", "timothy1"), ("디모데후서", "timothy2"),
    ("디도서", "titus"), ("빌레몬서", "philemon"), ("히브리서", "hebrews"),
    ("야고보서", "james"), ("베드로전서", "peter1"), ("베드로후서", "peter2"),
    ("요한일서", "john1"), ("요한이서", "john2"), ("요한삼서", "john3"),
    ("유다서", "jude"), ("요한계시록", "revelation"),
    ("통합복음서", "harmony"),
    ("토빗기", "tobit"), ("유딧기", "judith"),
    ("마카베오기상권", "maccabees1"), ("마카베오기하권", "maccabees2"),
    ("지혜서", "wisdom"), ("집회서", "sirach"), ("바룩서", "baruch"),
    ("다니엘추가", "danielExtra"), ("에스테르추가", "estherExtra"),
]

# Reuse adult emoji from build_web.py
import importlib.util
spec = importlib.util.spec_from_file_location("bw", ROOT / "build/build_web.py")
bw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bw)


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Very simple frontmatter parser (key: value or YAML list)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_text, body = m.group(1), m.group(2)
    fm: dict = {}
    current_key = None
    for line in fm_text.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_key and isinstance(fm.get(current_key), list):
                fm[current_key].append(line[4:].strip().strip('"'))
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"')
            if not val:
                fm[key] = []
                current_key = key
            else:
                fm[key] = val
                current_key = None
    return fm, body


def emit(slug: str, book_ko: str, fm: dict, body: str) -> str:
    bookName = book_ko.replace('상권', ' 상권').replace('하권', ' 하권').replace('추가', ' 추가') \
        if book_ko in ('마카베오기상권', '마카베오기하권', '다니엘추가', '에스테르추가') else book_ko
    bookName_map = {
        '마카베오기상권': '마카베오기 상권',
        '마카베오기하권': '마카베오기 하권',
        '다니엘추가': '다니엘 추가',
        '에스테르추가': '에스테르 추가',
    }
    bookName = bookName_map.get(book_ko, book_ko)

    # Default emoji from BOOKS map (use a fallback per-book emoji here)
    emoji_map = {
        'genesis': '🌱', 'exodus': '🌊', 'leviticus': '🔥', 'numbers': '🏕️',
        'deuteronomy': '📜', 'joshua': '⚔️', 'judges': '⚖️', 'ruth': '🌾',
        'samuel1': '👑', 'samuel2': '🎵', 'kings1': '🏛️', 'kings2': '🪦',
        'chronicles1': '📖', 'chronicles2': '🛐', 'ezra': '🔨', 'nehemiah': '🧱',
        'esther': '👰', 'job': '🌪️', 'psalms': '🎶', 'proverbs': '🦉',
        'ecclesiastes': '🌬️', 'song': '💋', 'isaiah': '🌟', 'jeremiah': '😢',
        'lamentations': '💔', 'ezekiel': '🛞', 'daniel': '🦁', 'hosea': '💍',
        'joel': '🦗', 'amos': '🐂', 'obadiah': '🦅', 'jonah': '🐳',
        'micah': '⛰️', 'nahum': '⚒️', 'habakkuk': '❓', 'zephaniah': '🔔',
        'haggai': '🏗️', 'zechariah': '🐎', 'malachi': '☀️',
        'matthew': '✝️', 'mark': '🦁', 'luke': '🐂', 'john': '🦅',
        'acts': '🕊️', 'romans': '⚖️', 'corinthians1': '💌', 'corinthians2': '💪',
        'galatians': '🕊️', 'ephesians': '🛡️', 'philippians': '😊', 'colossians': '👑',
        'thessalonians1': '🌅', 'thessalonians2': '⏳', 'timothy1': '📜', 'timothy2': '🏃',
        'titus': '👤', 'philemon': '🤝', 'hebrews': '🕯️', 'james': '🌿',
        'peter1': '🪨', 'peter2': '⏳', 'john1': '💕', 'john2': '✉️',
        'john3': '🤲', 'jude': '⚔️', 'revelation': '🐉', 'harmony': '✨',
        'tobit': '🐟', 'judith': '🌟', 'maccabees1': '🕎', 'maccabees2': '🕯️',
        'wisdom': '💡', 'sirach': '📜', 'baruch': '🌿',
        'danielExtra': '🦁', 'estherExtra': '👑',
    }
    emoji = emoji_map.get(slug, '📖')

    title = fm.get('title', f"{bookName} 소개")
    parts = [
        '---',
        f'title: "{title}"',
        f'bookName: "{bookName}"',
        f'emoji: "{emoji}"',
    ]
    if fm.get('author'):
        parts.append(f'author: "{fm["author"]}"')
    if fm.get('era'):
        parts.append(f'era: "{fm["era"]}"')
    if isinstance(fm.get('themes'), list) and fm['themes']:
        parts.append('themes:')
        for t in fm['themes']:
            parts.append(f'  - "{t}"')
    parts.append('---')
    parts.append('')
    parts.append(body.strip())
    return '\n'.join(parts) + '\n'


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    count = 0
    for book_ko, slug in BOOKS:
        src = ROOT / book_ko / 'intro.md'
        if not src.exists():
            continue
        text = src.read_text(encoding='utf-8')
        fm, body = parse_frontmatter(text)
        out = emit(slug, book_ko, fm, body)
        (DST / f'{slug}.md').write_text(out, encoding='utf-8')
        count += 1
    print(f"Synced {count} introductions")


if __name__ == '__main__':
    main()

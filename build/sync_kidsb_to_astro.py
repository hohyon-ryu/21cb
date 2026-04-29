#!/usr/bin/env python3
"""kidsb/<책>/Nx장.md → astro/src/content/kidsb-<slug>/0N.md 동기화.

- H1 → frontmatter (chapter, title, emoji)
- 유니코드 윗첨자 → 일반 숫자
- **N** 또는 **N-M** → <sup class="verse">N</sup>
- **bold** → <strong>
- 본문 톤 유지 (이모지, 어린이 어미 그대로)
"""
import importlib.util
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "kidsb"
DST = ROOT / "astro/src/content"

# 기존 성인용 장별 이모지 매핑 재활용
spec = importlib.util.spec_from_file_location("bw", ROOT / "build/build_web.py")
bw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bw)
ADULT_EMOJI = bw.CHAPTER_EMOJI_BY_BOOK

# 어린이용으로 부드럽게 바꿀 이모지 (필요한 것만 오버라이드)
KIDS_OVERRIDE: dict[str, dict[int, str]] = {
    "창세기": {
        4: "😢",   # 가인과 아벨 — 🩸 대신
        19: "🌆",  # 소돔 — 🔥 대신
        38: "👜",  # 다말 — 어린이용 부드럽게
    },
}

BOOKS = [
    ("창세기", "kidsb-genesis"),
    ("출애굽기", "kidsb-exodus"),
    ("레위기", "kidsb-leviticus"),
    ("민수기", "kidsb-numbers"),
    ("신명기", "kidsb-deuteronomy"),
    ("여호수아", "kidsb-joshua"),
    ("사사기", "kidsb-judges"),
    ("룻기", "kidsb-ruth"),
    ("사무엘상", "kidsb-samuel1"),
    ("사무엘하", "kidsb-samuel2"),
    ("열왕기상", "kidsb-kings1"),
    ("열왕기하", "kidsb-kings2"),
    ("역대상", "kidsb-chronicles1"),
    ("역대하", "kidsb-chronicles2"),
    ("에스라", "kidsb-ezra"),
    ("느헤미야", "kidsb-nehemiah"),
    ("에스더", "kidsb-esther"),
    ("욥기", "kidsb-job"),
    ("시편", "kidsb-psalms"),
    ("잠언", "kidsb-proverbs"),
    ("전도서", "kidsb-ecclesiastes"),
    ("아가", "kidsb-song"),
    ("이사야", "kidsb-isaiah"),
    ("예레미야", "kidsb-jeremiah"),
    ("예레미야애가", "kidsb-lamentations"),
    ("에스겔", "kidsb-ezekiel"),
    ("다니엘", "kidsb-daniel"),
    ("호세아", "kidsb-hosea"),
    ("요엘", "kidsb-joel"),
    ("아모스", "kidsb-amos"),
    ("오바댜", "kidsb-obadiah"),
    ("요나", "kidsb-jonah"),
    ("미가", "kidsb-micah"),
    ("나훔", "kidsb-nahum"),
    ("하박국", "kidsb-habakkuk"),
    ("스바냐", "kidsb-zephaniah"),
    ("학개", "kidsb-haggai"),
    ("스가랴", "kidsb-zechariah"),
    ("말라기", "kidsb-malachi"),
    ("마태복음", "kidsb-matthew"),
    ("마가복음", "kidsb-mark"),
    ("누가복음", "kidsb-luke"),
    ("요한복음", "kidsb-john"),
    ("사도행전", "kidsb-acts"),
    ("로마서", "kidsb-romans"),
    ("고린도전서", "kidsb-corinthians1"),
    ("고린도후서", "kidsb-corinthians2"),
    ("갈라디아서", "kidsb-galatians"),
    ("에베소서", "kidsb-ephesians"),
    ("빌립보서", "kidsb-philippians"),
    ("골로새서", "kidsb-colossians"),
    ("데살로니가전서", "kidsb-thessalonians1"),
    ("데살로니가후서", "kidsb-thessalonians2"),
    ("디모데전서", "kidsb-timothy1"),
    ("디모데후서", "kidsb-timothy2"),
    ("디도서", "kidsb-titus"),
    ("빌레몬서", "kidsb-philemon"),
    ("히브리서", "kidsb-hebrews"),
    ("야고보서", "kidsb-james"),
    ("베드로전서", "kidsb-peter1"),
    ("베드로후서", "kidsb-peter2"),
    ("요한일서", "kidsb-john1"),
    ("요한이서", "kidsb-john2"),
    ("요한삼서", "kidsb-john3"),
    ("유다서", "kidsb-jude"),
    ("요한계시록", "kidsb-revelation"),
    ("토빗기", "kidsb-tobit"),
    ("유딧기", "kidsb-judith"),
    ("마카베오기상권", "kidsb-maccabees1"),
    ("마카베오기하권", "kidsb-maccabees2"),
    ("지혜서", "kidsb-wisdom"),
    ("집회서", "kidsb-sirach"),
    ("바룩서", "kidsb-baruch"),
    ("다니엘추가", "kidsb-danielExtra"),
    ("에스테르추가", "kidsb-estherExtra"),
]

SUPER_TO_NORMAL = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
H1_RE = re.compile(r"^#\s+.+?\s+(\d+)(?:장|편)\s*[—–-]\s*(.+?)\s*$", re.MULTILINE)
VERSE_RE = re.compile(r"^\*\*([\d\-]+)\*\*\s*", re.MULTILINE)


def is_stub(text: str) -> bool:
    return "준비 중" in text or len(text.strip().splitlines()) < 5


def emoji_for(book_ko: str, chap: int) -> str:
    override = KIDS_OVERRIDE.get(book_ko, {}).get(chap)
    if override:
        return override
    return ADULT_EMOJI.get(book_ko, {}).get(chap, "📖")


def convert(text: str, default_emoji: str) -> tuple[int, str] | None:
    m = H1_RE.search(text)
    if not m:
        return None
    chap = int(m.group(1))
    title = m.group(2).strip()
    body = text[: m.start()] + text[m.end() :]
    body = re.sub(r"^\n+", "", body)
    body = body.translate(SUPER_TO_NORMAL)
    body = VERSE_RE.sub(r'<sup class="verse">\1</sup> ', body)
    body = re.sub(r"\*\*([^*\n]+?)\*\*", r"<strong>\1</strong>", body)
    body = re.sub(r"(\d)~(\d)", r"\1–\2", body)
    safe_title = title.replace('"', '\\"')
    front = (
        "---\n"
        f"chapter: {chap}\n"
        f'title: "{safe_title}"\n'
        f'emoji: "{default_emoji}"\n'
        "---\n\n"
    )
    return chap, front + body


def sync_book(book_ko: str, slug: str) -> int:
    src_dir = SRC / book_ko
    if not src_dir.exists():
        return 0
    out_dir = DST / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for src in sorted(src_dir.glob("*장.md")):
        text = src.read_text(encoding="utf-8")
        if is_stub(text):
            continue
        m = H1_RE.search(text)
        if not m:
            print(f"  ! skip {src.name} (no H1)")
            continue
        chap_for_emoji = int(m.group(1))
        result = convert(text, emoji_for(book_ko, chap_for_emoji))
        if result is None:
            continue
        chap, content = result
        out_path = out_dir / f"{chap:02d}.md"
        out_path.write_text(content, encoding="utf-8")
        count += 1
    return count


def main() -> None:
    for book_ko, slug in BOOKS:
        n = sync_book(book_ko, slug)
        if n > 0:
            print(f"{book_ko} → {slug}: {n} chapters")


if __name__ == "__main__":
    main()

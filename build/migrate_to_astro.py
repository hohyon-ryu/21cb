#!/usr/bin/env python3
"""기존 책별 마크다운을 Astro content collection으로 이식.

- 창세기/01장.md → astro/src/content/genesis/01.md (with frontmatter)
- 출애굽기/01장.md → astro/src/content/exodus/01.md
- H1 → frontmatter (title), body에서 제거
- 유니코드 윗첨자 → 일반 숫자
- **N** → <sup class="verse">N</sup>
- ../assets/ → /assets/
- 스텁 장(준비 중) 제외
"""
import importlib.util
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# build_web.py의 CHAPTER_EMOJI_BY_BOOK 가져오기
spec = importlib.util.spec_from_file_location("bw", ROOT / "build/build_web.py")
bw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bw)
EMOJI = bw.CHAPTER_EMOJI_BY_BOOK

SUPER_TO_NORMAL = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
VERSE_RE = re.compile(r"^\*\*(\d+)\*\*\s*", re.MULTILINE)
H1_RE = re.compile(r"^#\s+(\S+)\s+(\d+)(?:장|편)\s*[—–-]\s*(.+?)\s*$", re.MULTILINE)
TAIL_ITALIC_RE = re.compile(r"^(.+?)(?<!\*)\s+\*([^*]{12,}?)\*\s*$")


def _split_tail_italic(text: str) -> str:
    out = []
    for line in text.split("\n"):
        m = TAIL_ITALIC_RE.match(line)
        if m and not line.lstrip().startswith(">"):
            out.append(m.group(1).rstrip())
            out.append("")
            out.append(f"> *{m.group(2)}*")
        else:
            out.append(line)
    return "\n".join(out)

BOOKS = [
    ("창세기", "genesis"),
    ("출애굽기", "exodus"),
    ("레위기", "leviticus"),
    ("민수기", "numbers"),
    ("신명기", "deuteronomy"),
    ("여호수아", "joshua"),
    ("사사기", "judges"),
    ("룻기", "ruth"),
    ("사무엘상", "samuel1"),
    ("사무엘하", "samuel2"),
    ("열왕기상", "kings1"),
    ("열왕기하", "kings2"),
    ("역대상", "chronicles1"),
    ("역대하", "chronicles2"),
    ("에스라", "ezra"),
    ("느헤미야", "nehemiah"),
    ("에스더", "esther"),
    ("욥기", "job"),
    ("시편", "psalms"),
    ("잠언", "proverbs"),
    ("전도서", "ecclesiastes"),
    ("아가", "song"),
    ("이사야", "isaiah"),
    ("예레미야", "jeremiah"),
    ("예레미야애가", "lamentations"),
    ("에스겔", "ezekiel"),
    ("다니엘", "daniel"),
    ("호세아", "hosea"),
    ("요엘", "joel"),
    ("아모스", "amos"),
    ("오바댜", "obadiah"),
    ("요나", "jonah"),
    ("미가", "micah"),
    ("나훔", "nahum"),
    ("하박국", "habakkuk"),
    ("스바냐", "zephaniah"),
    ("학개", "haggai"),
    ("스가랴", "zechariah"),
    ("말라기", "malachi"),
    ("마태복음", "matthew"),
    ("마가복음", "mark"),
    ("누가복음", "luke"),
    ("요한복음", "john"),
    ("사도행전", "acts"),
    ("로마서", "romans"),
    ("고린도전서", "corinthians1"),
    ("고린도후서", "corinthians2"),
]


def is_stub(text: str) -> bool:
    return "준비 중" in text or len(text.strip().splitlines()) < 5


def migrate(book_ko: str, slug: str) -> int:
    src_dir = ROOT / book_ko
    out_dir = ROOT / "astro/src/content" / slug
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
        chap = int(m.group(2))
        title = m.group(3).strip()
        emoji = EMOJI.get(book_ko, {}).get(chap, "")
        body = text[: m.start()] + text[m.end() :]
        body = re.sub(r"^\n+", "", body)
        body = body.translate(SUPER_TO_NORMAL)
        body = VERSE_RE.sub(r'<sup class="verse">\1</sup> ', body)
        # 인라인 **bold** → <strong>: ) 또는 한글 인접 시 markdown 처리 실패하는 경우 회피
        body = re.sub(r"\*\*([^*\n]+?)\*\*", r"<strong>\1</strong>", body)
        # 숫자 사이 물결(1~7장)이 GFM 취소선으로 파싱되는 문제 방지
        body = re.sub(r"(\d)~(\d)", r"\1–\2", body)
        # 단락 끝 부연 italic을 별도 blockquote로 분리
        body = _split_tail_italic(body)
        body = body.replace("../assets/", "/assets/")
        safe_title = title.replace('"', '\\"')
        front = (
            "---\n"
            f"chapter: {chap}\n"
            f'title: "{safe_title}"\n'
            f'emoji: "{emoji}"\n'
            "---\n\n"
        )
        out_path = out_dir / f"{chap:02d}.md"
        out_path.write_text(front + body, encoding="utf-8")
        count += 1
    return count


def main() -> None:
    for book_ko, slug in BOOKS:
        n = migrate(book_ko, slug)
        print(f"{book_ko} → {slug}: {n} chapters")


if __name__ == "__main__":
    main()

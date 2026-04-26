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
H1_RE = re.compile(r"^#\s+(\S+)\s+(\d+)장\s*[—–-]\s*(.+?)\s*$", re.MULTILINE)

BOOKS = [
    ("창세기", "genesis"),
    ("출애굽기", "exodus"),
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

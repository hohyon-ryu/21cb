#!/usr/bin/env python3
"""21세기 성경 — 책 단위 PDF 빌더 (전 권 지원).

Usage:
  python3 build_pdf_book.py <한글책명>            # 전 장
  python3 build_pdf_book.py <한글책명> 1          # 1장만 샘플
  python3 build_pdf_book.py <한글책명> 1 5        # 1~5장

예:
  python3 build_pdf_book.py 창세기
  python3 build_pdf_book.py 마태복음
  python3 build_pdf_book.py 룻기
"""
import sys
import re
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
CSS = BUILD / "style.css"

H1_RE = re.compile(r"^#\s*\S+\s*(\d+)장\s*[—\-–]\s*(.+)\s*$")
SUPER_TO_NORMAL = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def list_chapters(book_dir: Path) -> list[int]:
    chaps = []
    for f in sorted(book_dir.glob("*장.md")):
        m = re.match(r"(\d+)장\.md$", f.name)
        if m:
            chaps.append(int(m.group(1)))
    return sorted(chaps)


def read_chapter_titles(book_dir: Path, chapters: list[int]) -> dict[int, str]:
    titles: dict[int, str] = {}
    for i in chapters:
        f = book_dir / f"{i:02d}장.md"
        if not f.exists():
            continue
        first = f.read_text(encoding="utf-8").splitlines()[0]
        m = H1_RE.match(first)
        if m:
            titles[i] = m.group(2).strip()
    return titles


def md_to_html(md_text: str, resource_path: str) -> str:
    res = subprocess.run(
        [
            "pandoc",
            "--from=markdown+smart",
            "--to=html5",
            "--no-highlight",
            "--resource-path", resource_path,
        ],
        input=md_text,
        capture_output=True,
        text=True,
        check=True,
    )
    return res.stdout.translate(SUPER_TO_NORMAL)


def build_cover_html(book_ko: str) -> str:
    return f"""
<div class="cover">
  <div class="ornament">✦ ✦ ✦</div>
  <div class="subtitle">21 세 기 에 &nbsp; 읽 는</div>
  <div class="main-title">성 경</div>
  <div class="divider"></div>
  <div class="booktitle">{'  '.join(book_ko)}</div>
  <div class="divider"></div>
</div>
"""


def build_toc_html(book_ko: str, titles: dict[int, str]) -> str:
    items = "".join(
        f'<li><span class="ch-num">{i}장</span><span class="ch-title">{titles.get(i, "")}</span></li>'
        for i in sorted(titles)
    )
    return f"""
<div class="toc">
  <h1>목 차</h1>
  <div class="part">
    <div class="part-header">
      <div class="part-title">{book_ko}</div>
    </div>
    <ul>{items}</ul>
  </div>
</div>
"""


def build_chapter_html(book_dir: Path, idx: int, resource_path: str) -> str:
    md = (book_dir / f"{idx:02d}장.md").read_text(encoding="utf-8")
    html = md_to_html(md, resource_path)
    return f'<div class="chapter">\n{html}\n</div>\n'


def build_full_html(book_ko: str, book_dir: Path, chapters: list[int], titles: dict[int, str]) -> str:
    css_text = CSS.read_text(encoding="utf-8")
    resource_path = os.pathsep.join([str(book_dir), str(ROOT), str(ROOT / "assets")])
    parts = [
        "<!DOCTYPE html>",
        '<html lang="ko">',
        "<head>",
        '<meta charset="UTF-8">',
        f"<title>21세기에 읽는 성경 · {book_ko}</title>",
        f"<style>\n{css_text}\n</style>",
        "</head>",
        "<body>",
        build_cover_html(book_ko),
        build_toc_html(book_ko, titles),
    ]
    for i in chapters:
        parts.append(build_chapter_html(book_dir, i, resource_path))
    parts.extend(["</body>", "</html>"])
    return "\n".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    book_ko = sys.argv[1]
    book_dir = ROOT / book_ko
    if not book_dir.exists():
        print(f"책 폴더 없음: {book_dir}")
        sys.exit(1)
    all_chapters = list_chapters(book_dir)
    if not all_chapters:
        print(f"{book_ko}에 *장.md 파일이 없음")
        sys.exit(1)

    if len(sys.argv) == 2:
        chapters = all_chapters
        out_name = f"{book_ko}_전권.pdf"
    elif len(sys.argv) == 3:
        n = int(sys.argv[2])
        chapters = [n]
        out_name = f"{book_ko}_{n:02d}장_샘플.pdf"
    elif len(sys.argv) == 4:
        a, b = int(sys.argv[2]), int(sys.argv[3])
        chapters = [c for c in all_chapters if a <= c <= b]
        out_name = f"{book_ko}_{a:02d}-{b:02d}장.pdf"
    else:
        print(__doc__)
        sys.exit(1)

    titles = read_chapter_titles(book_dir, chapters)
    html = build_full_html(book_ko, book_dir, chapters, titles)
    html_path = BUILD / "preview.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"HTML: {html_path}")

    pdf_path = BUILD / out_name
    print(f"PDF 생성 중 → {pdf_path}")
    subprocess.run(["weasyprint", str(html_path), str(pdf_path)], check=True)
    print(f"완료: {pdf_path}")


if __name__ == "__main__":
    main()

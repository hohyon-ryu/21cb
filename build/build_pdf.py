#!/usr/bin/env python3
"""
21세기에 읽는 성경 — 창세기 PDF 빌더
Usage:
  python3 build_pdf.py            # 전체 1~50장
  python3 build_pdf.py 1          # 1장만 샘플
  python3 build_pdf.py 1 5        # 1~5장 샘플
"""
import sys
import re
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CH_DIR = ROOT / "창세기"
BUILD = ROOT / "build"
CSS = BUILD / "style.css"
RESOURCE_PATH = os.pathsep.join([str(CH_DIR), str(ROOT), str(ROOT / "assets")])

CHAPTER_TITLES = {}  # 1: "세상이 만들어진 6일", ...


def read_chapter_titles():
    for i in range(1, 51):
        f = CH_DIR / f"{i:02d}장.md"
        if not f.exists():
            continue
        first_line = f.read_text(encoding="utf-8").splitlines()[0]
        m = re.match(r"#\s*창세기\s*\d+장\s*[—\-]\s*(.+)", first_line)
        CHAPTER_TITLES[i] = m.group(1).strip() if m else ""


def md_to_html_via_pandoc(md_text: str) -> str:
    result = subprocess.run(
        [
            "pandoc",
            "--from=markdown+smart",
            "--to=html5",
            "--no-highlight",
            "--resource-path", RESOURCE_PATH,
        ],
        input=md_text,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


SUPER_TO_NORMAL = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def post_process_chapter_html(html: str) -> str:
    """유니코드 상첨자를 일반 숫자로 치환 (CSS에서 위첨자 처리)"""
    return html.translate(SUPER_TO_NORMAL)


def build_cover_html() -> str:
    return """
<div class="cover">
  <div class="ornament">✦ ✦ ✦</div>
  <div class="subtitle">21 세 기 에 &nbsp; 읽 는</div>
  <div class="main-title">성 경</div>
  <div class="divider"></div>
  <div class="booktitle">창 세 기</div>
  <div class="divider"></div>
  <div class="meta">
    <em>아무것도 없을 때, 하나님이 세상을 만드셨다.</em>
  </div>
</div>
"""


PARTS = [
    {
        "num": "1부",
        "title": "원역사",
        "subtitle": "인류 전체의 시작",
        "range": (1, 11),
    },
    {
        "num": "2부",
        "title": "아브라함",
        "subtitle": "떠남, 별 같은 자손, 모리아의 결박",
        "range": (12, 25),
    },
    {
        "num": "3부",
        "title": "이삭과 야곱",
        "subtitle": "빼앗은 축복, 사닥다리, 얍복강의 씨름",
        "range": (26, 36),
    },
    {
        "num": "4부",
        "title": "요셉",
        "subtitle": "형들의 배신, 노예에서 이집트의 2인자로",
        "range": (37, 50),
    },
]


def build_toc_html(chapters: list[int]) -> str:
    chap_set = set(chapters)
    parts_html = []
    for part in PARTS:
        a, b = part["range"]
        items = []
        for i in range(a, b + 1):
            if i not in chap_set:
                continue
            title = CHAPTER_TITLES.get(i, "")
            items.append(
                f'<li><span class="ch-num">{i}장</span>'
                f'<span class="ch-title">{title}</span></li>'
            )
        if not items:
            continue
        parts_html.append(f"""
<div class="part">
  <div class="part-header">
    <div class="part-num">{part['num']}</div>
    <div class="part-title">{part['title']}<span class="part-range">{a}~{b}장</span></div>
    <div class="part-subtitle">{part['subtitle']}</div>
  </div>
  <ul>
    {''.join(items)}
  </ul>
</div>
""")
    return f"""
<div class="toc">
  <h1>목 차</h1>
  {''.join(parts_html)}
</div>
"""


def build_chapter_html(idx: int) -> str:
    f = CH_DIR / f"{idx:02d}장.md"
    md_text = f.read_text(encoding="utf-8")
    html = md_to_html_via_pandoc(md_text)
    html = post_process_chapter_html(html)
    return f'<div class="chapter">\n{html}\n</div>\n'


def build_full_html(chapters: list[int]) -> str:
    css_content = CSS.read_text(encoding="utf-8")
    parts = [
        "<!DOCTYPE html>",
        '<html lang="ko">',
        "<head>",
        '<meta charset="UTF-8">',
        "<title>21세기에 읽는 성경 · 창세기</title>",
        f"<style>\n{css_content}\n</style>",
        "</head>",
        "<body>",
        build_cover_html(),
        build_toc_html(chapters),
    ]
    for i in chapters:
        parts.append(build_chapter_html(i))
    parts.extend(["</body>", "</html>"])
    return "\n".join(parts)


def main():
    read_chapter_titles()

    if len(sys.argv) == 1:
        chapters = list(range(1, 51))
        out_name = "창세기_전권.pdf"
    elif len(sys.argv) == 2:
        n = int(sys.argv[1])
        chapters = [n]
        out_name = f"창세기_{n:02d}장_샘플.pdf"
    elif len(sys.argv) == 3:
        a, b = int(sys.argv[1]), int(sys.argv[2])
        chapters = list(range(a, b + 1))
        out_name = f"창세기_{a:02d}-{b:02d}장.pdf"
    else:
        print("Usage: python3 build_pdf.py [start] [end]")
        sys.exit(1)

    html = build_full_html(chapters)
    html_path = BUILD / "preview.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"HTML 생성: {html_path}")

    pdf_path = BUILD / out_name
    print(f"PDF 변환 중... → {pdf_path}")
    subprocess.run(
        ["weasyprint", str(html_path), str(pdf_path)],
        check=True,
    )
    print(f"완료: {pdf_path}")


if __name__ == "__main__":
    main()

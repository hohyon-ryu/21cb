#!/usr/bin/env python3
"""21세기 성경 — 웹 리더 빌더.

Usage:
  python3 build/build_web.py             # 창세기 → site/web/index.html
  python3 build/build_web.py 출애굽기     # 출애굽기 → site/web/exodus/index.html
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_NAME = sys.argv[1] if len(sys.argv) > 1 else "창세기"
CH_DIR = ROOT / SRC_NAME

# 창세기는 site/web/index.html 그대로(레거시 경로 유지). 다른 책은 하위 폴더.
SLUG = {
    "창세기": "",
    "창세기_초등": "kids",
    "출애굽기": "exodus",
    "레위기": "leviticus",
    "민수기": "numbers",
}.get(SRC_NAME, SRC_NAME.lower())
OUT = ROOT / "site/web" / SLUG / "index.html" if SLUG else ROOT / "site/web/index.html"

SUPER_TO_NORMAL = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
VERSE_RE = re.compile(r"^\*\*(\d+)\*\*\s*", re.MULTILINE)

# 책별 장 이모지 — 본문 내용이 결정되면 채워 넣음
CHAPTER_EMOJI_BY_BOOK = {
    "창세기": {
        1: "🌍", 2: "🌳", 3: "🐍", 4: "🩸", 5: "📜",
        6: "🌧️", 7: "🌊", 8: "🕊️", 9: "🌈", 10: "🌐",
        11: "🗼", 12: "🐪", 13: "⛺", 14: "⚔️", 15: "⭐",
        16: "💧", 17: "✍️", 18: "🍞", 19: "🔥", 20: "👑",
        21: "👶", 22: "🐏", 23: "🕯️", 24: "💍", 25: "🍲",
        26: "👣", 27: "🦌", 28: "🪜", 29: "🌙", 30: "🐑",
        31: "🏃", 32: "🤼", 33: "🤝", 34: "😢", 35: "🌟",
        36: "🏔️", 37: "💭", 38: "👰", 39: "🔒", 40: "🍷",
        41: "🌾", 42: "🥖", 43: "👦", 44: "🥃", 45: "😭",
        46: "👨‍👩‍👧‍👦", 47: "🌱", 48: "🤲", 49: "🦁", 50: "🪦",
    },
    "출애굽기": {
        1: "👑", 2: "👶", 3: "🔥", 4: "🐍", 5: "🧱",
        6: "📜", 7: "🩸", 8: "🐸", 9: "🌩️", 10: "🦗",
        11: "⚠️", 12: "🐑", 13: "🍞", 14: "🌊", 15: "🎵",
        16: "🍞", 17: "💧", 18: "🤝", 19: "⛰️", 20: "📜",
        21: "⚖️", 22: "⚖️", 23: "🎉", 24: "📜", 25: "⛺",
        26: "⛺", 27: "🔥", 28: "👔", 29: "🕯️", 30: "🕯️",
        31: "🛌", 32: "🐂", 33: "😇", 34: "📜", 35: "🛌",
        36: "⚒️", 37: "⛺", 38: "🔥", 39: "👔", 40: "✨",
    },
    "레위기": {
        1: "🔥", 2: "🌾", 3: "🤝", 4: "🩸", 5: "⚖️",
        6: "🕯️", 7: "🍖", 8: "👔", 9: "🐑", 10: "⚡",
        11: "🐂", 12: "👶", 13: "🩹", 14: "🌿", 15: "💧",
        16: "🐐", 17: "🩸", 18: "💔", 19: "✨", 20: "⚖️",
        21: "👤", 22: "🍞", 23: "📅", 24: "🕯️", 25: "🎺",
        26: "⚔️", 27: "🤲",
    },
    "민수기": {
        1: "🔢", 2: "⛺", 3: "🛐", 4: "🪔", 5: "🌿",
        6: "🌾", 7: "🎁", 8: "🕯️", 9: "🌑", 10: "🎺",
        11: "🦃", 12: "😢", 13: "🍇", 14: "⚡", 15: "📜",
        16: "🔥", 17: "🌳", 18: "🍞", 19: "🐄", 20: "💧",
        21: "🐍", 22: "🐴", 23: "⭐", 24: "⭐", 25: "⚔️",
        26: "🔢", 27: "👧", 28: "📅", 29: "📅", 30: "🤲",
        31: "⚔️", 32: "🐑", 33: "🛤️", 34: "🗺️", 35: "🏛️",
        36: "💍",
    },
}
CHAPTER_EMOJI = CHAPTER_EMOJI_BY_BOOK.get(SRC_NAME, {})

CHAPTER_H1_RE = re.compile(
    rf'<h1 id="({re.escape(SRC_NAME)}-(\d+)장-[^"]+)">\s*'
    rf'{re.escape(SRC_NAME)}\s+\d+장\s*[—–-]\s*([\s\S]+?)\s*</h1>'
)


def prepare(text: str) -> str:
    text = text.translate(SUPER_TO_NORMAL)
    text = VERSE_RE.sub(r'<sup class="verse">\1</sup> ', text)
    return text


def is_stub(text: str) -> bool:
    """본문이 작성되지 않은 placeholder 장. 빌드에서 제외."""
    return "준비 중" in text or len(text.strip().splitlines()) < 5


def decorate_chapter_titles(html: str) -> str:
    def repl(m: re.Match) -> str:
        cid = m.group(1)
        num = int(m.group(2))
        title = re.sub(r"\s+", " ", m.group(3)).strip()
        emoji = CHAPTER_EMOJI.get(num, "")
        return (
            f'<h1 id="{cid}" class="chapter-title">'
            f'<span class="ch-emoji" aria-hidden="true">{emoji}</span>'
            f'<span class="ch-num">{SRC_NAME} {num}장</span>'
            f'<span class="ch-title">{title}</span>'
            f"</h1>"
        )

    return CHAPTER_H1_RE.sub(repl, html)


def main() -> None:
    if not CH_DIR.exists():
        raise SystemExit(f"Not found: {CH_DIR}")

    OUT.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        chapters = []
        for src in sorted(CH_DIR.glob("*.md")):
            text = src.read_text(encoding="utf-8")
            if is_stub(text):
                continue
            (tmp / src.name).write_text(prepare(text), encoding="utf-8")
            chapters.append(str(tmp / src.name))

        if not chapters:
            raise SystemExit(f"No chapters with content in {CH_DIR}")

        # CSS 경로: 창세기는 web.css(같은 폴더), 다른 책은 ../web.css 상위 참조
        css_path = "web.css" if not SLUG else "../web.css"

        cmd = [
            "pandoc", "-s",
            "--from=markdown+smart",
            "--to=html5",
            "--metadata", f"title=21세기 성경 · {SRC_NAME}",
            "--metadata", "lang=ko",
            "--css", css_path,
            "--resource-path", f"{CH_DIR}:{ROOT / 'assets'}",
            "-o", str(OUT),
        ] + chapters

        print(f"Building {OUT.relative_to(ROOT)} from {len(chapters)} chapters...")
        subprocess.run(cmd, check=True)
        OUT.write_text(decorate_chapter_titles(OUT.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"Done ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
21세기에 읽는 성경 — 창세기 EPUB 빌더
Usage:
  python3 build_epub.py                       # 기본: 창세기/ → 창세기.epub
  python3 build_epub.py 창세기_초등 창세기_초등.epub
"""
import re
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
CSS = BUILD / "epub.css"

if len(sys.argv) >= 3:
    SRC_NAME = sys.argv[1]
    OUT_NAME = sys.argv[2]
elif len(sys.argv) == 2:
    SRC_NAME = sys.argv[1]
    OUT_NAME = f"{SRC_NAME}.epub"
else:
    SRC_NAME = "창세기"
    OUT_NAME = "창세기.epub"

CH_DIR = ROOT / SRC_NAME
OUT = BUILD / OUT_NAME

if not CH_DIR.exists():
    print(f"오류: 폴더가 없습니다: {CH_DIR}")
    sys.exit(1)

SUPER_TO_NORMAL = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")

PARTS = [
    {"num": "1부", "title": "원역사", "subtitle": "인류 전체의 시작",
     "range": (1, 11)},
    {"num": "2부", "title": "아브라함", "subtitle": "떠남, 별 같은 자손, 모리아의 결박",
     "range": (12, 25)},
    {"num": "3부", "title": "이삭과 야곱", "subtitle": "빼앗은 축복, 사닥다리, 얍복강의 씨름",
     "range": (26, 36)},
    {"num": "4부", "title": "요셉", "subtitle": "형들의 배신, 노예에서 이집트의 2인자로",
     "range": (37, 50)},
]


def get_edition_label() -> str:
    if "초등" in SRC_NAME or "kid" in SRC_NAME.lower():
        return "초등학생을 위한 쉬운 번역본"
    return "현대 번역본 (중학생 수준)"


def make_intro_md() -> str:
    """표지 + 조망 페이지를 마크다운으로 작성."""
    edition = get_edition_label()
    is_kids = "초등" in SRC_NAME

    parts_md = []
    for p in PARTS:
        a, b = p["range"]
        parts_md.append(
            f"### {p['num']} · {p['title']} ({a}~{b}장)\n\n"
            f"*{p['subtitle']}*\n"
        )

    if is_kids:
        opening = "*아무것도 없을 때, 하나님이 세상을 만드셨어요.*"
        intro_text = "창세기는 크게 두 부분이에요. 앞쪽 1~11장은 온 세상이 어떻게 시작됐는지를, 뒤쪽 12~50장은 아브라함부터 요셉까지 한 가족의 이야기를 들려줘요."
    else:
        opening = "*아무것도 없을 때, 하나님이 세상을 만드셨다.*"
        intro_text = "창세기는 두 부분으로 나뉜다. 앞 11장은 인류 전체의 시작을, 뒤 39장은 한 가문(아브라함부터 요셉까지)에 내려진 약속을 다룬다."

    return f"""---
title: 창세기
subtitle: 21세기에 읽는 성경 — {edition}
lang: ko
---

# 창세기

**21세기에 읽는 성경 — {edition}**

{opening}

---

## 창세기 조망

{intro_text}

{chr(10).join(parts_md)}
"""


def strip_blockquotes(text: str) -> str:
    """마크다운 `>` 인용 기호를 모두 제거 — 일반 본문으로 평탄화."""
    out = []
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("> "):
            indent = line[: len(line) - len(stripped)]
            out.append(indent + stripped[2:])
        elif stripped.startswith(">"):
            indent = line[: len(line) - len(stripped)]
            out.append(indent + stripped[1:])
        else:
            out.append(line)
    return "\n".join(out)


def convert_verse_numbers(text: str) -> str:
    """줄 시작의 **숫자**를 <sup class="verse">숫자</sup>로 변환."""
    return re.sub(
        r"^\*\*(\d+)\*\*\s*",
        r'<sup class="verse">\1</sup> ',
        text,
        flags=re.MULTILINE,
    )


def prepare_chapter_md(idx: int, tmpdir: Path) -> Path:
    """원본 마크다운: 유니코드 상첨자 → 일반 숫자 → <sup> + blockquote 평탄화."""
    src = CH_DIR / f"{idx:02d}장.md"
    text = src.read_text(encoding="utf-8")
    text = text.translate(SUPER_TO_NORMAL)
    text = strip_blockquotes(text)
    text = convert_verse_numbers(text)
    dst = tmpdir / f"{idx:02d}장.md"
    dst.write_text(text, encoding="utf-8")
    return dst


def main():
    with tempfile.TemporaryDirectory() as td:
        tmpdir = Path(td)

        intro_path = tmpdir / "00_intro.md"
        intro_path.write_text(make_intro_md(), encoding="utf-8")

        chapter_paths = [
            prepare_chapter_md(i, tmpdir)
            for i in range(1, 51)
            if (CH_DIR / f"{i:02d}장.md").exists()
        ]

        edition = get_edition_label()
        resource_path = os.pathsep.join([str(CH_DIR), str(ROOT), str(ROOT / "assets")])
        cmd = [
            "pandoc",
            "-o", str(OUT),
            "--from=markdown+smart",
            "--to=epub3",
            "--metadata", "title=창세기",
            "--metadata", f"subtitle=21세기에 읽는 성경 — {edition}",
            "--metadata", f"creator=21세기에 읽는 성경 ({edition})",
            "--metadata", "lang=ko",
            "--css", str(CSS),
            "--toc",
            "--toc-depth=1",
            "--split-level=1",
            "--resource-path", resource_path,
            str(intro_path),
        ] + [str(p) for p in chapter_paths]

        print("EPUB 빌드 중...")
        subprocess.run(cmd, check=True)
        size_mb = OUT.stat().st_size / (1024 * 1024)
        print(f"완료: {OUT} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()

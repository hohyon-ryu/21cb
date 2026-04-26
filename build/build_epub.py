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
    return "현대 번역본"


BOOK_INTROS = {
    "창세기": {
        "opening": "*아무것도 없을 때, 하나님이 세상을 만드셨다.*",
        "overview": "창세기는 두 부분으로 나뉜다. 앞 11장은 인류 전체의 시작을, 뒤 39장은 한 가문(아브라함부터 요셉까지)에 내려진 약속을 다룬다.",
        "parts": PARTS,
    },
    "창세기_초등": {
        "opening": "*아무것도 없을 때, 하나님이 세상을 만드셨어요.*",
        "overview": "창세기는 크게 두 부분이에요. 앞쪽 1~11장은 온 세상이 어떻게 시작됐는지를, 뒤쪽 12~50장은 아브라함부터 요셉까지 한 가족의 이야기를 들려줘요.",
        "parts": PARTS,
    },
    "출애굽기": {
        "opening": "*노예의 땅에서 자유의 산까지 — 한 민족이 만들어진 책.*",
        "overview": "출애굽기는 야곱의 일흔 명이 한 민족이 되어 가는 책이다. 이집트의 압제, 모세의 부르심, 열 가지 재앙, 홍해 도하, 시내산의 언약, 그리고 광야 한가운데 세워진 성막 — 한 책 안에 해방의 서사와 거룩의 청사진이 함께 있다.",
        "parts": [
            {"num": "1부", "title": "출애굽", "subtitle": "압제, 모세, 재앙, 홍해", "range": (1, 18)},
            {"num": "2부", "title": "시내 언약", "subtitle": "십계명과 언약법전", "range": (19, 24)},
            {"num": "3부", "title": "성막", "subtitle": "설계, 금송아지, 건축, 영광", "range": (25, 40)},
        ],
    },
    "레위기": {
        "opening": "*거룩한 분 가까이에서 — 어떻게 살 것인가.*",
        "overview": "레위기는 출애굽기 끝에 세워진 성막에서, 광야 한가운데 임한 거룩과 어떻게 함께 살 것인가에 대한 책이다. 다섯 가지 제사, 제사장 위임, 정한 것과 부정한 것, 거룩 법전, 절기, 희년 — 일상의 모든 결을 거룩의 자리에 두는 안내서다.",
        "parts": [
            {"num": "1부", "title": "제사", "subtitle": "다섯 제사와 제사장 위임", "range": (1, 10)},
            {"num": "2부", "title": "정결", "subtitle": "음식, 몸, 피부", "range": (11, 16)},
            {"num": "3부", "title": "거룩 법전", "subtitle": "이웃 사랑, 절기, 희년", "range": (17, 27)},
        ],
    },
    "민수기": {
        "opening": "*시내산을 떠나 약속의 땅 앞까지 — 광야 40년의 책.*",
        "overview": "민수기는 시내산을 떠난 이스라엘이 가나안 문턱까지 가는 길을 적는다. 두 번의 인구조사 사이에, 한 세대가 통째로 광야에서 사라지고 새 세대가 일어선다. 정탐꾼의 두려움, 고라의 반역, 발람의 예언, 놋뱀, 슬로브핫 딸들의 상속권 — 약속을 향해 걸으면서 만난 사건들이 한 책에 모인다.",
        "parts": [
            {"num": "1부", "title": "시내산에서", "subtitle": "인구조사, 진영, 출발 준비", "range": (1, 10)},
            {"num": "2부", "title": "광야의 위기", "subtitle": "원망, 정탐, 반역, 40년 형벌", "range": (11, 25)},
            {"num": "3부", "title": "새 세대", "subtitle": "두 번째 인구조사, 도피성, 약속의 문턱", "range": (26, 36)},
        ],
    },
}


def make_intro_md() -> str:
    """표지 + 조망 페이지를 마크다운으로 작성."""
    edition = get_edition_label()
    info = BOOK_INTROS.get(SRC_NAME, BOOK_INTROS["창세기"])
    book_label = SRC_NAME.replace("_초등", " (초등)")

    parts_md = []
    for p in info.get("parts", []):
        a, b = p["range"]
        parts_md.append(
            f"### {p['num']} · {p['title']} ({a}~{b}장)\n\n"
            f"*{p['subtitle']}*\n"
        )

    return f"""---
title: {book_label}
subtitle: 21세기에 읽는 성경 — {edition}
lang: ko
---

# {book_label}

**21세기에 읽는 성경 — {edition}**

{info['opening']}

---

## {book_label} 조망

{info['overview']}

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
        # 책별 표지 이미지 — 같은 톤의 아카이벌 지도
        COVERS = {
            "창세기": "assets/maps/genesis/01_eden_and_four_rivers.png",
            "출애굽기": "assets/maps/genesis/11_joseph_route_to_egypt.png",
            "레위기": "assets/maps/genesis/03_flood_to_ararat.png",
            "민수기": "assets/maps/genesis/04_babel_and_dispersion.png",
        }
        cover_rel = COVERS.get(SRC_NAME, "assets/maps/genesis/01_eden_and_four_rivers.png")
        cover = ROOT / cover_rel
        title_meta = SRC_NAME.replace("_초등", "(초등)")
        cmd = [
            "pandoc",
            "-o", str(OUT),
            "--from=markdown+smart",
            "--to=epub3",
            "--metadata", f"title={title_meta}",
            "--metadata", f"subtitle=21세기에 읽는 성경 — {edition}",
            "--metadata", f"creator=21세기에 읽는 성경 ({edition})",
            "--metadata", "lang=ko",
            "--css", str(CSS),
            "--epub-cover-image", str(cover),
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

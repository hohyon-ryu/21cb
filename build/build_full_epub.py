#!/usr/bin/env python3
"""21세기에 읽는 성경 — 66권 전체 EPUB 빌더.

Usage:
  python3 build/build_full_epub.py

산출물: build/21세기성경_전체.epub
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
CSS = BUILD / "epub.css"
OUT = BUILD / "21세기성경_전체.epub"

sys.path.insert(0, str(BUILD))
from build_epub import (  # noqa: E402
    SUPER_TO_NORMAL, BOOK_INTROS, strip_blockquotes, convert_verse_numbers,
    get_book_cover_path, make_cover_md,
)

BOOKS_ORDER = [
    "창세기", "출애굽기", "레위기", "민수기", "신명기",
    "여호수아", "사사기", "룻기", "사무엘상", "사무엘하",
    "열왕기상", "열왕기하", "역대상", "역대하", "에스라",
    "느헤미야", "에스더", "욥기", "시편", "잠언",
    "전도서", "아가", "이사야", "예레미야", "예레미야애가",
    "에스겔", "다니엘", "호세아", "요엘", "아모스",
    "오바댜", "요나", "미가", "나훔", "하박국",
    "스바냐", "학개", "스가랴", "말라기",
    "마태복음", "마가복음", "누가복음", "요한복음", "사도행전",
    "로마서", "고린도전서", "고린도후서", "갈라디아서", "에베소서",
    "빌립보서", "골로새서", "데살로니가전서", "데살로니가후서", "디모데전서",
    "디모데후서", "디도서", "빌레몬서", "히브리서", "야고보서",
    "베드로전서", "베드로후서", "요한일서", "요한이서", "요한삼서",
    "유다서", "요한계시록",
]

OT_BOOKS = set(BOOKS_ORDER[:39])

CHAPTER_RE = re.compile(r"^(\d+)장\.md$")


def make_master_intro() -> str:
    return """---
title: 21세기에 읽는 성경
subtitle: 구약 39권 + 신약 27권 — 현대 번역본 합본
lang: ko
---

# 21세기에 읽는 성경

**구약 39권 + 신약 27권 합본**

*에덴에서 시작해 새 예루살렘으로 끝나는 한 이야기.*

---

## 이 책에 대하여

성경 66권 전체를 현대 한국어로 번역하고 부연 설명을 붙인 합본이다. 본문은 짧은 문장과 일상의 어휘를 사용했고, 각 장 아래에는 어원·고대 근동 사회 배경·고고학적 발견·세 종교(유대·기독·이슬람) 해석 차이·신약과 구약의 인용 관계 등을 함께 적었다.

권별 EPUB도 따로 받을 수 있다. 합본은 통독을 위한 한 권이다.
"""


def make_book_intro(book_ko: str) -> str:
    """책별 표지 페이지를 한 장(level 1)으로."""
    info = BOOK_INTROS.get(book_ko)
    if not info:
        return f"# {book_ko}\n\n"
    parts_md = []
    for p in info.get("parts", []):
        a, b = p["range"]
        parts_md.append(
            f"### {p['num']} · {p['title']} ({a}~{b}장)\n\n"
            f"*{p['subtitle']}*\n"
        )
    return (
        f"{make_cover_md(book_ko)}"
        f"# {book_ko}\n\n"
        f"{info['opening']}\n\n"
        f"---\n\n"
        f"## {book_ko} 조망\n\n"
        f"{info['overview']}\n\n"
        f"{chr(10).join(parts_md)}\n"
    )


def prepare_chapter(idx: int, src_dir: Path, tmpdir: Path, prefix: str) -> Path:
    """원본 마크다운을 평탄화하고 절 번호를 변환. H1을 ## (level 2)로 강등."""
    src = src_dir / f"{idx:02d}장.md"
    text = src.read_text(encoding="utf-8")
    text = text.translate(SUPER_TO_NORMAL)
    text = strip_blockquotes(text)
    text = convert_verse_numbers(text)
    # H1을 H2로 강등 — 책 표지가 H1이므로 장은 H2여야 함
    text = re.sub(r"^# ", "## ", text, count=1, flags=re.MULTILINE)
    dst = tmpdir / f"{prefix}_{idx:02d}.md"
    dst.write_text(text, encoding="utf-8")
    return dst


def main():
    with tempfile.TemporaryDirectory() as td:
        tmpdir = Path(td)

        files = []

        # 마스터 표지
        intro_path = tmpdir / "00_master_intro.md"
        intro_path.write_text(make_master_intro(), encoding="utf-8")
        files.append(intro_path)

        # 구약/신약 섹션 표지
        ot_section = tmpdir / "00_ot_section.md"
        ot_section.write_text("# 오랜 약속 (구약 39권)\n\n*아담에서 말라기까지 — 약속의 책.*\n", encoding="utf-8")
        files.append(ot_section)

        for book_idx, book_ko in enumerate(BOOKS_ORDER):
            # 신약 섹션 표지 삽입
            if book_ko == "마태복음":
                nt_section = tmpdir / "00_nt_section.md"
                nt_section.write_text("# 새 약속 (신약 27권)\n\n*그리스도와 함께 시작된 새로운 이야기.*\n", encoding="utf-8")
                files.append(nt_section)

            src_dir = ROOT / book_ko
            if not src_dir.exists():
                print(f"  ! 스킵: {book_ko} (폴더 없음)")
                continue

            # 책별 표지
            book_intro_path = tmpdir / f"{book_idx + 10:02d}_{book_ko}_intro.md"
            book_intro_path.write_text(make_book_intro(book_ko), encoding="utf-8")
            files.append(book_intro_path)

            # 장 파일들
            chapter_files = sorted(
                src_dir.glob("*장.md"),
                key=lambda p: int(CHAPTER_RE.match(p.name).group(1)) if CHAPTER_RE.match(p.name) else 0,
            )
            count = 0
            for src in chapter_files:
                m = CHAPTER_RE.match(src.name)
                if not m:
                    continue
                idx = int(m.group(1))
                files.append(prepare_chapter(idx, src_dir, tmpdir, f"{book_idx + 10:02d}_{book_ko}"))
                count += 1
            print(f"  {book_ko}: {count} 장")

        resource_paths = [str(ROOT), str(ROOT / "astro/public")] + [
            str(ROOT / b) for b in BOOKS_ORDER if (ROOT / b).exists()
        ]
        cover = get_book_cover_path("창세기")
        cmd = [
            "pandoc",
            "-o", str(OUT),
            "--from=markdown+smart",
            "--to=epub3",
            "--metadata", "title=21세기에 읽는 성경",
            "--metadata", "subtitle=구약 39권 + 신약 27권 합본",
            "--metadata", "creator=21세기에 읽는 성경 (현대 번역본)",
            "--metadata", "lang=ko",
            "--css", str(CSS),
            "--toc",
            "--toc-depth=2",
            "--split-level=1",
            "--resource-path", os.pathsep.join(resource_paths),
        ] + [str(f) for f in files]

        if cover:
            toc_idx = cmd.index("--toc")
            cmd[toc_idx:toc_idx] = ["--epub-cover-image", str(cover)]

        print(f"\nEPUB 빌드 중... ({len(files)} 파일)")
        subprocess.run(cmd, check=True)
        size_mb = OUT.stat().st_size / (1024 * 1024)
        print(f"완료: {OUT} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()

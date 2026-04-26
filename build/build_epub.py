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
    "사무엘상": {
        "opening": "*마지막 사사, 첫 왕 — 한 시대가 끝나고 다른 시대가 열린다.*",
        "overview": "사무엘상은 한나의 기도에서 시작된다. 마지막 사사 사무엘이 자라고, 이스라엘의 요청으로 첫 왕 사울이 세워지고, 사울이 무너지고, 다윗이 기름부음을 받고 광야에서 도망 다니며 단련된다. 사울의 길보아 산 자결로 끝나는, 두 왕의 교차 서사.",
        "parts": [
            {"num": "1부", "title": "사무엘", "subtitle": "한나의 기도, 어린 사무엘, 언약궤", "range": (1, 7)},
            {"num": "2부", "title": "사울", "subtitle": "왕 요청, 즉위, 첫 패배", "range": (8, 15)},
            {"num": "3부", "title": "다윗의 도망", "subtitle": "골리앗, 사울의 시기, 광야 생활", "range": (16, 31)},
        ],
    },
    "역대상": {
        "opening": "*포로 귀환 후 다시 쓰인 다윗의 이야기 — 성전 중심의 재해석.*",
        "overview": "역대상은 사무엘서·열왕기와 같은 시대를 다루지만, 포로 귀환 공동체가 다시 쓴 신학적 재해석이다. 9장에 걸친 족보로 시작해 사울의 죽음과 다윗 왕국 전체를 다루되, 다윗의 어두운 면(밧세바·압살롬)은 빠지고 성전 준비와 예배 조직이 강조된다. 마지막 장에서 다윗이 솔로몬에게 성전 청사진과 모든 자재를 인계한다.",
        "parts": [
            {"num": "1부", "title": "족보", "subtitle": "아담부터 귀환 공동체까지", "range": (1, 9)},
            {"num": "2부", "title": "다윗의 즉위와 정복", "subtitle": "헤브론·예루살렘·블레셋", "range": (10, 20)},
            {"num": "3부", "title": "성전 준비", "subtitle": "타작마당, 자재, 레위인 조직, 청사진 인계", "range": (21, 29)},
        ],
    },
    "역대하": {
        "opening": "*솔로몬에서 포로까지 — 유다 왕국의 신학적 회고.*",
        "overview": "역대하는 솔로몬의 즉위·성전 건축에서 시작해 남왕국 유다의 모든 왕을 다룬다(북왕국은 거의 빠진다). 마지막 장에서 예루살렘 함락과 함께 페르시아 고레스의 칙령 — 귀환과 성전 재건 명령 — 으로 끝난다. 한 시대의 종말이 새 시대의 약속과 겹치는 결말.",
        "parts": [
            {"num": "1부", "title": "솔로몬", "subtitle": "지혜·성전·시바 여왕", "range": (1, 9)},
            {"num": "2부", "title": "분열 후 유다", "subtitle": "르호보암부터 아하스까지", "range": (10, 28)},
            {"num": "3부", "title": "개혁과 멸망", "subtitle": "히스기야·요시야·바벨론, 고레스 칙령", "range": (29, 36)},
        ],
    },
    "열왕기상": {
        "opening": "*솔로몬의 영광에서 분열까지 — 한 왕국이 둘로 갈라진 책.*",
        "overview": "열왕기상은 솔로몬의 즉위·성전 건축·세계 명성에서 시작해, 그의 우상숭배와 사후 왕국이 북왕국 이스라엘과 남왕국 유다로 갈라지는 과정을 다룬다. 후반부는 두 왕국의 왕들 — 특히 북왕국 아합과 이세벨, 그리고 그들과 맞선 예언자 엘리야 — 의 격렬한 충돌이 무대다. 갈멜산의 불, 사르밧 과부, 호렙의 세미한 음성, 나봇의 포도원이 모두 여기 있다.",
        "parts": [
            {"num": "1부", "title": "솔로몬", "subtitle": "지혜, 성전, 왕궁, 시바 여왕", "range": (1, 11)},
            {"num": "2부", "title": "분열", "subtitle": "여로보암과 르호보암, 북·남 두 왕국", "range": (12, 16)},
            {"num": "3부", "title": "엘리야 시대", "subtitle": "갈멜산, 호렙, 나봇의 포도원", "range": (17, 22)},
        ],
    },
    "열왕기하": {
        "opening": "*두 왕국의 멸망 — 북은 아시리아에, 남은 바벨론에.*",
        "overview": "열왕기하는 엘리야의 회오리바람 승천에서 시작해, 엘리사의 기적, 두 왕국의 흥망, 북왕국의 BC 722년 아시리아 멸망, 남왕국의 BC 587년 바벨론 멸망과 예루살렘 성전 파괴까지 다룬다. 히스기야의 산헤립 침공 격퇴, 요시야의 율법책 발견과 개혁, 마지막 왕 시드기야의 눈이 뽑히는 장면 — 한 민족의 정치적 종말과 신학적 진단이 함께 기록된다.",
        "parts": [
            {"num": "1부", "title": "엘리사", "subtitle": "회오리바람, 기적들, 예후의 혁명", "range": (1, 13)},
            {"num": "2부", "title": "북왕국 멸망", "subtitle": "아시리아의 칼, 사마리아 함락(BC 722)", "range": (14, 17)},
            {"num": "3부", "title": "남왕국의 마지막", "subtitle": "히스기야, 요시야, 바벨론 포로(BC 587)", "range": (18, 25)},
        ],
    },
    "사무엘하": {
        "opening": "*다윗의 왕국 — 영광과 추락이 한 사람 안에서.*",
        "overview": "사무엘하는 다윗의 통일 왕국 전체를 다룬다. 사울의 죽음 애도에서 시작해, 헤브론·예루살렘 두 단계의 즉위, 언약궤 운반과 다윗 언약, 밧세바 사건과 그 대가로 무너지는 가족 — 암논의 강간, 압살롬의 반역, 세바의 봉기, 마지막 인구조사까지. 한 인간 안의 빛과 어둠이 가장 정직하게 기록된 책.",
        "parts": [
            {"num": "1부", "title": "왕좌", "subtitle": "헤브론, 예루살렘, 언약궤", "range": (1, 10)},
            {"num": "2부", "title": "추락", "subtitle": "밧세바, 암논, 압살롬", "range": (11, 19)},
            {"num": "3부", "title": "마무리", "subtitle": "세바, 시편, 인구조사", "range": (20, 24)},
        ],
    },
    "룻기": {
        "opening": "*베들레헴의 추수 들판 — 한 이방 여인의 헌신.*",
        "overview": "룻기는 사사 시대를 배경으로 한 4장의 짧은 가족 이야기다. 모압 출신 룻이 시어머니 나오미를 따라 베들레헴으로 돌아오고, 친족 보아스와의 결혼으로 이어진다. 그 사이에서 태어난 오벳이 다윗의 할아버지가 된다. 사사기의 어둠 한가운데 놓인 빛, 이방 여인이 메시아 계보로 들어오는 통로.",
        "parts": [
            {"num": "전체", "title": "룻기", "subtitle": "헌신·이삭 줍기·기업 무를 자·다윗의 할머니", "range": (1, 4)},
        ],
    },
    "사사기": {
        "opening": "*왕이 없던 시절 — 사람마다 자기 눈에 옳은 대로.*",
        "overview": "사사기는 여호수아 사후, 왕정이 시작되기 전의 어두운 막간이다. 이스라엘이 가나안 신들에게 빠져들고, 외세의 압제 아래 놓이고, 부르짖으면 사사가 일어나 구원하고, 다시 타락하는 — 죄/형벌/회개/구원의 순환이 일곱 번 반복된다. 옷니엘·에훗·드보라·기드온·입다·삼손, 그리고 마지막의 끔찍한 두 부록(미가의 우상, 베냐민 학살). '왕이 없으므로 사람마다 자기 눈에 옳은 대로 행하였다.'",
        "parts": [
            {"num": "1부", "title": "정복의 미완성", "subtitle": "남은 가나안, 타락의 시작", "range": (1, 3)},
            {"num": "2부", "title": "큰 사사들", "subtitle": "드보라, 기드온, 입다, 삼손", "range": (4, 16)},
            {"num": "3부", "title": "두 개의 부록", "subtitle": "미가의 우상, 베냐민의 만행", "range": (17, 21)},
        ],
    },
    "여호수아": {
        "opening": "*요단강을 건너 — 약속의 땅을 손에 넣다.*",
        "overview": "여호수아는 모세 사후 새 지도자가 요단강을 건너 가나안을 정복하고 열두 지파에 땅을 분배하는 책이다. 라합의 신앙, 무너지는 여리고 성벽, 아이성의 패배와 회복, 기브온과의 속임수 조약, 멈춘 태양, 가나안 분배, 마지막 세겜 언약까지 — 약속의 성취와 동시에 새 책임의 시작을 다룬다.",
        "parts": [
            {"num": "1부", "title": "강을 건너", "subtitle": "여호수아 임직, 라합, 요단 도하", "range": (1, 5)},
            {"num": "2부", "title": "정복", "subtitle": "여리고, 아이, 기브온, 멈춘 태양", "range": (6, 12)},
            {"num": "3부", "title": "분배", "subtitle": "지파별 영토 할당, 도피성, 레위 성읍", "range": (13, 21)},
            {"num": "4부", "title": "마지막 언약", "subtitle": "동편 지파 귀환, 세겜 갱신", "range": (22, 24)},
        ],
    },
    "신명기": {
        "opening": "*요단강 건너기 직전 — 모세의 마지막 설교.*",
        "overview": "신명기는 모세가 가나안 진입을 앞둔 새 세대에게 들려준 마지막 설교 모음이다. 광야 40년을 회고하고, 십계명과 율법을 다시 풀어주고, 축복과 저주의 양 갈래를 제시한다. 이름의 뜻 그대로 '두 번째 율법'(deutero-nomos) — 같은 율법을 새 세대의 언어로 다시 설교한 책이다. 모세는 약속의 땅을 보지만 들어가지 못하고 느보산에서 죽는다.",
        "parts": [
            {"num": "1부", "title": "회고", "subtitle": "광야 40년의 되짚기", "range": (1, 4)},
            {"num": "2부", "title": "재선포", "subtitle": "십계명, 쉐마, 핵심 율법", "range": (5, 11)},
            {"num": "3부", "title": "법전", "subtitle": "예배·전쟁·재판·일상의 규례", "range": (12, 26)},
            {"num": "4부", "title": "언약과 마지막", "subtitle": "축복과 저주, 모세의 노래, 느보산", "range": (27, 34)},
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
            "신명기": "assets/maps/genesis/05_abram_first_journey.png",
            "여호수아": "assets/maps/genesis/06_kings_war_and_promise_land.png",
            "사사기": "assets/maps/genesis/07_patriarch_centers_hebron_beersheba_moriah.png",
            "룻기": "assets/maps/genesis/08_rebekah_route_aram_to_canaan.png",
            "사무엘상": "assets/maps/genesis/09_jacob_flight_and_return.png",
            "사무엘하": "assets/maps/genesis/10_shechem_bethel_seir.png",
            "열왕기상": "assets/maps/genesis/02_east_of_eden_and_nod.png",
            "열왕기하": "assets/maps/genesis/04_babel_and_dispersion.png",
            "역대상": "assets/maps/genesis/01_eden_and_four_rivers.png",
            "역대하": "assets/maps/genesis/03_flood_to_ararat.png",
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

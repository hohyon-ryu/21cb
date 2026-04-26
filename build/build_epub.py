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
    "이사야": {
        "opening": "*예루살렘의 가장 큰 예언자 — 위로하라, 위로하라.*",
        "overview": "이사야는 BC 8세기 예루살렘 예언자에서 시작해 포로기·귀환기까지를 아우르는 66장의 거대한 책. 처음 39장은 심판의 분위기, 40장부터는 위로의 분위기. '한 어린 아이가 우리를 위해 났다'(9:6), '고난의 종'(53장), '새 하늘 새 땅'(65-66장) — 신약이 가장 자주 인용한 구약 책.",
        "parts": [
            {"num": "1부", "title": "심판과 약속", "subtitle": "예루살렘·임마누엘·이방 심판", "range": (1, 39)},
            {"num": "2부", "title": "위로의 책", "subtitle": "포로 위로·고난의 종·새 하늘", "range": (40, 66)},
        ],
    },
    "예레미야": {
        "opening": "*우는 예언자 — 예루살렘의 마지막 40년.*",
        "overview": "예레미야는 요시야 13년(BC 627)부터 예루살렘 함락 후 이집트 망명까지 활동한 예언자. 토기장이의 비유, 깨진 항아리, 새 언약(31:31-34), 시드기야의 눈이 뽑히는 장면, 바벨론 70년 — 한 민족의 종말을 가장 가까이서 본 자의 기록.",
        "parts": [
            {"num": "1부", "title": "초기 예언", "subtitle": "소명·항아리·성전 설교", "range": (1, 25)},
            {"num": "2부", "title": "고난과 환상", "subtitle": "예언자의 박해와 새 언약", "range": (26, 45)},
            {"num": "3부", "title": "이방 신탁과 함락", "subtitle": "열방 심판·예루살렘 멸망", "range": (46, 52)},
        ],
    },
    "예레미야애가": {
        "opening": "*불타 버린 도시 위의 다섯 노래 — 알파벳 두운의 통곡.*",
        "overview": "예레미야애가는 예루살렘 함락(BC 587) 직후의 다섯 편 시. 1·2·4장은 알파벳 22행 두운, 3장은 66행(각 글자 3행씩). 유대교는 매년 9월 9일(티샤 베아브)에 낭독한다. 가장 어두운 책 한가운데 '여호와의 인자와 긍휼이 새롭다'(3:22-23)가 빛난다.",
        "parts": [{"num": "전체", "title": "다섯 애가", "subtitle": "예루살렘 함락의 통곡", "range": (1, 5)}],
    },
    "에스겔": {
        "opening": "*포로지에서 본 환상들 — 마른 뼈가 살아나는 책.*",
        "overview": "에스겔은 1차 포로(BC 597) 때 바벨론으로 끌려간 제사장 출신. 그발 강가에서 본 네 생물과 바퀴, 예루살렘 성전을 떠나는 영광, 마른 뼈 골짜기, 곡과 마곡, 새 성전 환상 — 가장 환상적이고 묵시적인 예언서.",
        "parts": [
            {"num": "1부", "title": "심판 환상", "subtitle": "네 생물·성전 떠난 영광·예루살렘 함락", "range": (1, 24)},
            {"num": "2부", "title": "이방 신탁", "subtitle": "두로·이집트 등 일곱 민족", "range": (25, 32)},
            {"num": "3부", "title": "회복 환상", "subtitle": "마른 뼈·새 성전·생명의 강", "range": (33, 48)},
        ],
    },
    "다니엘": {
        "opening": "*바벨론 궁의 네 청년 — 사자 굴과 묵시.*",
        "overview": "다니엘은 1차 포로(BC 605)로 끌려간 청년. 전반 6장은 궁중 이야기(채소·금 신상·풀무불·꿈·벽의 글씨·사자 굴), 후반 6장은 묵시 환상(네 짐승·숫양과 숫염소·70주·마지막 환상). 구약과 신약을 잇는 가장 직접적인 다리 — '인자 같은 이'(7:13) → 예수의 자기 호칭.",
        "parts": [
            {"num": "1부", "title": "궁중 이야기", "subtitle": "채소·금 신상·사자 굴", "range": (1, 6)},
            {"num": "2부", "title": "환상", "subtitle": "네 짐승·70주·마지막 날", "range": (7, 12)},
        ],
    },
    "전도서": {
        "opening": "*해 아래 새것이 없다 — 전도자(코헬렛)의 회의 노트.*",
        "overview": "전도서는 자신을 '코헬렛'(모인 자들의 교사)이라 부르는 자의 기록이다. 부와 지혜와 쾌락과 일을 두루 시험한 끝에 '헤벨'(헛된 숨)이라는 결론으로 돌아온다. 그러나 결말은 회의가 아니라 '하나님을 경외하라'다. 욥기·잠언과 함께 지혜 문학의 세 정점.",
        "parts": [{"num": "전체", "title": "전도서", "subtitle": "헤벨의 12장", "range": (1, 12)}],
    },
    "아가": {
        "opening": "*가장 노골적인 사랑 노래 — 정경 안의 인간 욕망.*",
        "overview": "아가는 신랑·신부·예루살렘 처녀들의 대화로 짜인 사랑 시 모음이다. 본문에 하나님이 한 번도 등장하지 않으면서 정경에 들어온 책. 유대 전승은 야훼와 이스라엘의 사랑, 기독교 전승은 그리스도와 교회의 사랑으로 풀이해 왔으나 본문 자체는 두 인간의 노래다. 유월절에 낭독된다.",
        "parts": [{"num": "전체", "title": "아가", "subtitle": "8장의 사랑 시", "range": (1, 8)}],
    },
    "호세아": {
        "opening": "*고멜과 결혼한 예언자 — 부정한 사랑의 비유로 산 일생.*",
        "overview": "호세아는 북왕국의 마지막 예언자(BC 8세기). 음란한 여자 고멜과의 결혼이 야훼와 이스라엘의 관계를 그대로 비춘다. 자녀의 이름조차 메시지였다 — '이스르엘', '로루하마(긍휼받지 못함)', '로암미(내 백성이 아니다)'. 그러나 결말은 회복.",
        "parts": [
            {"num": "1부", "title": "고멜", "subtitle": "결혼 비유와 자녀 이름", "range": (1, 3)},
            {"num": "2부", "title": "고발과 회복", "subtitle": "북왕국의 죄와 야훼의 사랑", "range": (4, 14)},
        ],
    },
    "요엘": {
        "opening": "*메뚜기 떼가 다 먹어 치웠다 — 여호와의 날.*",
        "overview": "요엘은 메뚜기 재앙의 묘사로 시작해 '여호와의 날'을 선포한다. 사도행전 2장 베드로의 오순절 설교가 인용한 '내가 모든 육체에 내 영을 부어 주리라'(2:28-32)가 이 책에 있다.",
        "parts": [{"num": "전체", "title": "요엘", "subtitle": "메뚜기·영의 부음·심판의 날", "range": (1, 3)}],
    },
    "아모스": {
        "opening": "*드고아의 목자 — 정의가 강물처럼.*",
        "overview": "아모스는 남왕국 유다의 목자였으나 북왕국 베델에서 예언했다. 사회 정의의 가장 격렬한 외침. '오직 정의를 강같이 흐르게 하라.' 일곱 이방 민족 심판으로 시작해 자기 백성에게 칼을 돌린다.",
        "parts": [{"num": "전체", "title": "아모스", "subtitle": "이방 심판·이스라엘 고발·다섯 환상", "range": (1, 9)}],
    },
    "오바댜": {
        "opening": "*에돔에 대한 가장 짧은 책 — 형제의 배신을 잊지 마라.*",
        "overview": "오바댜는 구약에서 가장 짧은 책(21절). 에돔(에서의 후손)에 대한 심판 예언. 예루살렘 함락 때 약탈에 가담한 형제 민족에 대한 분노.",
        "parts": [{"num": "전체", "title": "오바댜", "subtitle": "한 장 안의 에돔 심판", "range": (1, 1)}],
    },
    "요나": {
        "opening": "*도망친 예언자 — 큰 물고기와 박 넝쿨.*",
        "overview": "요나는 니느웨로 가라는 명령을 받고 다시스로 도망친다. 폭풍, 큰 물고기, 토해냄, 회개한 니느웨, 그리고 박 넝쿨 아래 분노. 이방 도시의 회개와 한 예언자의 좁은 마음을 대조한 책. 예수가 자신의 부활 표적으로 인용.",
        "parts": [{"num": "전체", "title": "요나", "subtitle": "도망·물고기·니느웨·박넝쿨", "range": (1, 4)}],
    },
    "미가": {
        "opening": "*베들레헴에서 나올 한 분 — 정의·자비·겸손.*",
        "overview": "미가는 아모스와 동시대의 시골 예언자. 베들레헴에서 메시아가 나올 것을 예언(5:2 — 마태 2:6 인용). '정의·자비·겸손'(6:8) — 가장 자주 인용되는 미가의 한 절.",
        "parts": [{"num": "전체", "title": "미가", "subtitle": "심판·메시아·정의의 요약", "range": (1, 7)}],
    },
    "나훔": {
        "opening": "*니느웨의 멸망 — 요나가 외친 그 도시의 마지막.*",
        "overview": "나훔은 BC 612년 아시리아 수도 니느웨의 멸망을 미리 노래한다. 요나가 회개시킨 도시가 후대에 다시 부패하고, 결국 메대·바벨론 연합군에 무너진다.",
        "parts": [{"num": "전체", "title": "나훔", "subtitle": "니느웨의 마지막", "range": (1, 3)}],
    },
    "하박국": {
        "opening": "*왜 침묵하십니까 — 항변과 응답.*",
        "overview": "하박국은 야훼와 직접 대화하는 형식의 책이다. '의인은 그 믿음으로 살리라'(2:4) — 사도 바울이 로마서·갈라디아서에서 인용한 신약 신학의 토대 구절. 마지막 3장은 시.",
        "parts": [{"num": "전체", "title": "하박국", "subtitle": "두 항변·다섯 화·기도의 시", "range": (1, 3)}],
    },
    "스바냐": {
        "opening": "*여호와의 날 — 그러나 남은 자의 노래.*",
        "overview": "스바냐는 요시야 시대 예언자. 다가올 심판과 그 너머의 회복을 노래한다. 마지막은 '여호와께서 너로 인하여 기쁨을 이기지 못하시며'(3:17)의 사랑 노래.",
        "parts": [{"num": "전체", "title": "스바냐", "subtitle": "심판·이방·노래", "range": (1, 3)}],
    },
    "학개": {
        "opening": "*성전을 다시 지어라 — 두 장의 짧은 격려.*",
        "overview": "학개는 포로 귀환 후 침체된 성전 재건을 다시 일으키는 짧은 예언서. BC 520년 다리오 2년의 정확한 날짜로 시작.",
        "parts": [{"num": "전체", "title": "학개", "subtitle": "두 장의 격려", "range": (1, 2)}],
    },
    "스가랴": {
        "opening": "*여덟 환상과 메시아의 그림 — 구약의 묵시문학 정점.*",
        "overview": "스가랴는 학개와 동시대 예언자. 1-6장 여덟 환상, 7-8장 율법 회복, 9-14장 메시아 묵시. '나귀를 탄 왕'(9:9), '은 30조각'(11:12-13), '찔린 자를 바라봄'(12:10) 등 신약 수난 서사가 직접 인용한 텍스트.",
        "parts": [
            {"num": "1부", "title": "여덟 환상", "subtitle": "재건·정결·메시아", "range": (1, 8)},
            {"num": "2부", "title": "메시아 묵시", "subtitle": "나귀의 왕·은 30·찔린 자", "range": (9, 14)},
        ],
    },
    "말라기": {
        "opening": "*구약의 마지막 — 엘리야가 다시 올 것이다.*",
        "overview": "말라기는 구약 정경의 마지막 책. '내가 너를 사랑한다 / 너희가 어떻게 하셨느냐'의 여섯 변론. '엘리야가 다시 올 것'(4:5-6) — 신약이 세례 요한에게 적용한 그 예언.",
        "parts": [{"num": "전체", "title": "말라기", "subtitle": "여섯 변론과 엘리야 약속", "range": (1, 4)}],
    },
    "사도행전": {
        "opening": "*예루살렘에서 로마까지 — 한 운동이 어떻게 세상으로 퍼졌나.*",
        "overview": "사도행전은 누가복음의 후속편이다. 예수의 승천에서 시작해 오순절 성령강림, 베드로의 사역, 스데반 순교, 사울의 회심, 바울의 세 차례 선교 여행, 로마 압송으로 끝난다. 1세기 교회의 첫 30년을 추적한 유일한 역사 자료.",
        "parts": [
            {"num": "1부", "title": "예루살렘", "subtitle": "오순절·베드로·스데반·사울 회심", "range": (1, 12)},
            {"num": "2부", "title": "이방으로", "subtitle": "바울의 1·2·3차 선교 여행", "range": (13, 21)},
            {"num": "3부", "title": "로마로", "subtitle": "체포·재판·항해·로마 도착", "range": (22, 28)},
        ],
    },
    "로마서": {
        "opening": "*복음의 가장 체계적인 신학 — 바울의 대작.*",
        "overview": "로마서는 바울이 직접 가본 적 없는 로마 교회에 보낸 편지(AD 57년경). 자신의 복음을 가장 체계적으로 정리한 신학적 대작. '의인은 믿음으로 살리라'(1:17 — 하박국 인용)가 종교개혁의 토대. 1-11장 교리, 12-16장 실천.",
        "parts": [
            {"num": "1부", "title": "구원의 이치", "subtitle": "이신칭의·아담과 그리스도·성령", "range": (1, 8)},
            {"num": "2부", "title": "이스라엘과 이방", "subtitle": "선택과 자비", "range": (9, 11)},
            {"num": "3부", "title": "그리스도인의 삶", "subtitle": "산 제사·정부·약자 배려", "range": (12, 16)},
        ],
    },
    "고린도전서": {
        "opening": "*문제 많은 교회에 보낸 가장 실제적인 편지.*",
        "overview": "고린도전서는 바울이 에베소에서 고린도 교회에 보낸 편지(AD 55년경). 분쟁·근친상간·소송·결혼·우상 제물·예배 질서·은사·부활까지. 13장 사랑의 송가, 15장 부활의 신학이 정점.",
        "parts": [
            {"num": "1부", "title": "교회의 문제", "subtitle": "분파·도덕·소송·결혼", "range": (1, 7)},
            {"num": "2부", "title": "예배와 사랑", "subtitle": "우상 제물·만찬·은사·사랑", "range": (8, 14)},
            {"num": "3부", "title": "부활", "subtitle": "그리스도와 우리의 부활", "range": (15, 16)},
        ],
    },
    "고린도후서": {
        "opening": "*가장 개인적인 편지 — 사도의 약함과 자랑.*",
        "overview": "고린도후서는 격렬한 갈등 후 화해의 편지(AD 56년경). 바울의 가장 개인적인 글. 사역의 영광과 짐, 약함과 자랑, 가난한 자를 위한 헌금, 거짓 사도들과의 변증 — 사역의 정직한 풍경.",
        "parts": [
            {"num": "1부", "title": "화해와 사역", "subtitle": "위로·새 언약·약함의 영광", "range": (1, 7)},
            {"num": "2부", "title": "헌금", "subtitle": "예루살렘 가난한 자 모금", "range": (8, 9)},
            {"num": "3부", "title": "사도의 변증", "subtitle": "거짓 사도와의 대립", "range": (10, 13)},
        ],
    },
    "마태복음": {
        "opening": "*아브라함의 자손, 다윗의 아들 — 약속의 성취로 시작하는 첫 복음.*",
        "overview": "마태복음은 유대인 청중을 향해 쓰인 복음서다. 예수가 구약의 모든 약속을 성취하는 다윗의 메시아임을 다섯 강화(산상수훈·전도·비유·교회·종말)로 펼친다. 동방박사·이집트 피난·산상수훈·주기도문·팔복·대위임 — 가장 자주 인용되는 복음.",
        "parts": [
            {"num": "1부", "title": "왕의 등장", "subtitle": "탄생·세례·시험·산상수훈", "range": (1, 7)},
            {"num": "2부", "title": "왕의 사역", "subtitle": "기적·비유·제자 파송", "range": (8, 18)},
            {"num": "3부", "title": "왕의 길", "subtitle": "예루살렘·종말·고난·부활", "range": (19, 28)},
        ],
    },
    "마가복음": {
        "opening": "*가장 짧고 빠른 복음 — '곧'의 연속.*",
        "overview": "마가복음은 가장 짧고 가장 빠른 복음서다. '곧'(에위테우스)이 41회 등장. 베드로의 회상을 마가가 받아쓴 것으로 전승. 메시아 비밀 모티프 — 예수가 자기 정체를 종종 숨기심. 가이사랴 빌립보 고백(8장) 이후 십자가로 직진.",
        "parts": [
            {"num": "1부", "title": "갈릴리 사역", "subtitle": "세례·기적·비유·제자", "range": (1, 8)},
            {"num": "2부", "title": "예루살렘으로", "subtitle": "수난 예고·변화산·고난", "range": (9, 16)},
        ],
    },
    "누가복음": {
        "opening": "*가장 긴 복음 — 의사 누가의 정밀한 기록.*",
        "overview": "누가복음은 이방인 의사 누가가 데오빌로에게 헌정한 복음서. 마리아의 마그니피카트, 사가랴·시므온 노래, 베들레헴 마구간, 12세 예수의 성전 방문, 선한 사마리아인, 탕자, 부자와 나사로, 엠마오 — 누가만 기록한 비유와 사건들이 가장 풍부.",
        "parts": [
            {"num": "1부", "title": "탄생과 시작", "subtitle": "두 잉태·마구간·세례·시험", "range": (1, 4)},
            {"num": "2부", "title": "갈릴리 사역", "subtitle": "기적·비유·제자", "range": (5, 9)},
            {"num": "3부", "title": "예루살렘 여정", "subtitle": "선한 사마리아인·탕자·부자", "range": (10, 19)},
            {"num": "4부", "title": "수난과 부활", "subtitle": "최후 만찬·십자가·엠마오", "range": (20, 24)},
        ],
    },
    "요한복음": {
        "opening": "*태초에 말씀이 계셨다 — 가장 신학적인 복음.*",
        "overview": "요한복음은 다른 세 복음과 다른 시각의 복음서. 일곱 표적, 일곱 '나는 ~이다'(에고 에이미), 일곱 강화. 공관복음과 다른 시간선과 사건. 가나 혼인 잔치, 니고데모, 사마리아 여인, 죽은 나사로, 세족식, 보혜사 약속 — 요한만 기록한 깊은 신학.",
        "parts": [
            {"num": "1부", "title": "표적의 책", "subtitle": "일곱 표적·일곱 나는~이다", "range": (1, 12)},
            {"num": "2부", "title": "영광의 책", "subtitle": "세족·고별 강화·고난·부활", "range": (13, 21)},
        ],
    },
    "시편": {
        "opening": "*150편의 노래 — 인간이 하나님께 부른 모든 음역.*",
        "overview": "시편은 다윗을 비롯한 여러 저자들의 150편 시 모음이다. 찬양·탄원·감사·지혜·왕정·역사·순례 — 인간이 하나님 앞에서 가질 수 있는 거의 모든 마음이 여기 담겼다. 5권으로 나뉘며 각 권 끝에 송영. 시편 119편(가장 긴 장)부터 117편(가장 짧은 장)까지, 분노에서 환희까지 정직하게 기록된다.",
        "parts": [
            {"num": "1권", "title": "다윗의 시", "subtitle": "탄원과 신뢰", "range": (1, 41)},
            {"num": "2권", "title": "왕정 시", "subtitle": "예루살렘과 시온", "range": (42, 72)},
            {"num": "3권", "title": "성가대 시", "subtitle": "아삽과 고라 자손", "range": (73, 89)},
            {"num": "4권", "title": "왕이신 야훼", "subtitle": "야훼의 왕권 찬양", "range": (90, 106)},
            {"num": "5권", "title": "할렐", "subtitle": "찬양·순례·할렐루야", "range": (107, 150)},
        ],
    },
    "욥기": {
        "opening": "*아무 죄 없이 모든 것을 잃은 한 사람 — 고난 앞의 가장 정직한 책.*",
        "overview": "욥기는 의로운 한 사람이 모든 것을 잃은 채 친구 셋과 청년 엘리후, 그리고 마지막에 회오리바람의 하나님과 차례로 대화하는 시 형식의 책이다. '인과응보'라는 통념을 가장 격렬하게 흔드는 책. 답을 주지 않고 더 큰 질문으로 응답하는 결말 — 그러나 욥은 회복된다.",
        "parts": [
            {"num": "1부", "title": "재앙", "subtitle": "사탄의 시험, 모든 것의 상실", "range": (1, 3)},
            {"num": "2부", "title": "친구들과의 변론", "subtitle": "엘리바스·빌닷·소발 세 차례", "range": (4, 31)},
            {"num": "3부", "title": "엘리후", "subtitle": "젊은 청년의 새 관점", "range": (32, 37)},
            {"num": "4부", "title": "회오리바람과 회복", "subtitle": "야훼의 응답, 욥의 두 배", "range": (38, 42)},
        ],
    },
    "잠언": {
        "opening": "*지혜의 시작은 여호와를 경외함이라 — 일상의 신학.*",
        "overview": "잠언은 솔로몬과 후대 현자들의 짧은 격언 모음이다. 1-9장은 아버지가 아들에게 들려주는 긴 권면, 10-29장은 짧은 두 행 격언의 폭포, 30장은 아굴, 31장은 르무엘 왕의 어머니가 아들에게 한 말과 '현숙한 여인' 시. 추상 신학이 아니라 일상의 결단을 위한 지혜.",
        "parts": [
            {"num": "1부", "title": "지혜의 권면", "subtitle": "아들아, 들으라 — 긴 권면", "range": (1, 9)},
            {"num": "2부", "title": "솔로몬의 잠언", "subtitle": "두 행 격언의 폭포", "range": (10, 29)},
            {"num": "3부", "title": "아굴과 르무엘", "subtitle": "마지막 두 부록, 현숙한 여인", "range": (30, 31)},
        ],
    },
    "에스라": {
        "opening": "*폐허에서 두 번째 성전까지 — 70년 후의 귀향.*",
        "overview": "에스라는 페르시아 고레스의 칙령(BC 538)으로 시작된 두 차례의 귀환을 다룬다. 첫 귀환에서 스룹바벨이 두 번째 성전을 짓고, 80년 후 학자 에스라가 율법을 들고 와 이방 여인 결혼 문제를 다룬다. 정체성의 재구성, 율법 공동체의 부활.",
        "parts": [
            {"num": "1부", "title": "성전 재건", "subtitle": "스룹바벨, 폐허에서 다시", "range": (1, 6)},
            {"num": "2부", "title": "에스라의 개혁", "subtitle": "율법, 결혼, 회개", "range": (7, 10)},
        ],
    },
    "느헤미야": {
        "opening": "*폐허가 된 성벽 — 한 술 맡은 자가 일으킨 도시.*",
        "overview": "느헤미야는 페르시아 왕 아닥사스다의 술 맡은 자였다. 예루살렘 성벽이 무너졌다는 소식에 휴직하고 돌아와 52일 만에 성벽을 다시 세운다. 산발랏의 방해, 빈민의 빚 문제, 에스라와의 협력으로 율법을 함께 낭독, 그리고 마지막 안식일·결혼 개혁까지.",
        "parts": [
            {"num": "1부", "title": "성벽", "subtitle": "기도, 휴직, 52일", "range": (1, 7)},
            {"num": "2부", "title": "갱신", "subtitle": "율법 낭독, 언약 봉인", "range": (8, 13)},
        ],
    },
    "에스더": {
        "opening": "*하나님의 이름 한 번 안 나오는 책 — 그러나 가장 또렷한 섭리.*",
        "overview": "에스더는 페르시아 왕 아하수에로(크세르크세스) 시대 수산 궁의 한 유대인 여인 이야기다. 와스디의 폐위, 에스더의 등극, 하만의 음모, 모르드개의 거절, 두 잔치, 처형대의 역전 — 한 민족의 멸절 위기와 부림절의 기원. 본문 어디에도 하나님이 명시되지 않으나 모든 우연이 섭리로 짜인다.",
        "parts": [
            {"num": "전체", "title": "수산의 잔치", "subtitle": "와스디·에스더·하만·모르드개·부림절", "range": (1, 10)},
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
            "에스라": "assets/maps/genesis/05_abram_first_journey.png",
            "느헤미야": "assets/maps/genesis/06_kings_war_and_promise_land.png",
            "에스더": "assets/maps/genesis/07_patriarch_centers_hebron_beersheba_moriah.png",
            "욥기": "assets/maps/genesis/08_rebekah_route_aram_to_canaan.png",
            "시편": "assets/maps/genesis/10_shechem_bethel_seir.png",
            "잠언": "assets/maps/genesis/09_jacob_flight_and_return.png",
            "전도서": "assets/maps/genesis/10_shechem_bethel_seir.png",
            "아가": "assets/maps/genesis/02_east_of_eden_and_nod.png",
            "이사야": "assets/maps/genesis/01_eden_and_four_rivers.png",
            "예레미야": "assets/maps/genesis/04_babel_and_dispersion.png",
            "예레미야애가": "assets/maps/genesis/03_flood_to_ararat.png",
            "에스겔": "assets/maps/genesis/05_abram_first_journey.png",
            "다니엘": "assets/maps/genesis/06_kings_war_and_promise_land.png",
            "호세아": "assets/maps/genesis/04_babel_and_dispersion.png",
            "요엘": "assets/maps/genesis/03_flood_to_ararat.png",
            "아모스": "assets/maps/genesis/05_abram_first_journey.png",
            "오바댜": "assets/maps/genesis/06_kings_war_and_promise_land.png",
            "요나": "assets/maps/genesis/07_patriarch_centers_hebron_beersheba_moriah.png",
            "미가": "assets/maps/genesis/08_rebekah_route_aram_to_canaan.png",
            "나훔": "assets/maps/genesis/09_jacob_flight_and_return.png",
            "하박국": "assets/maps/genesis/10_shechem_bethel_seir.png",
            "스바냐": "assets/maps/genesis/01_eden_and_four_rivers.png",
            "학개": "assets/maps/genesis/02_east_of_eden_and_nod.png",
            "스가랴": "assets/maps/genesis/03_flood_to_ararat.png",
            "말라기": "assets/maps/genesis/04_babel_and_dispersion.png",
            "마태복음": "assets/maps/genesis/01_eden_and_four_rivers.png",
            "마가복음": "assets/maps/genesis/02_east_of_eden_and_nod.png",
            "누가복음": "assets/maps/genesis/03_flood_to_ararat.png",
            "요한복음": "assets/maps/genesis/04_babel_and_dispersion.png",
            "사도행전": "assets/maps/genesis/05_abram_first_journey.png",
            "로마서": "assets/maps/genesis/06_kings_war_and_promise_land.png",
            "고린도전서": "assets/maps/genesis/07_patriarch_centers_hebron_beersheba_moriah.png",
            "고린도후서": "assets/maps/genesis/08_rebekah_route_aram_to_canaan.png",
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

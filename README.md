# 21세기 성경 (21cb)

> 21세기에 읽는 한국어 성경. 어른용 새 번역, 어린이용, 개역한글, 천주교 외경 — 한 사이트에서 즉시 비교.

[![Deploy](https://github.com/hohyon-ryu/21cb/actions/workflows/deploy.yml/badge.svg)](https://github.com/hohyon-ryu/21cb/actions/workflows/deploy.yml)
[![Pages](https://img.shields.io/badge/site-21cb-blue)](https://hohyon-ryu.github.io/21cb/)
[![Code License: MIT](https://img.shields.io/badge/code-MIT-green.svg)](LICENSE)
[![Content License: CC BY-SA 4.0](https://img.shields.io/badge/content-CC--BY--SA--4.0-orange.svg)](LICENSE-CONTENT)

**Live**: https://hohyon-ryu.github.io/21cb/

---

## 무엇인가

성경 본문을 읽기 좋게 다시 정리한 정적 웹사이트. 한 사이트에 네 종류의 본문을 두고, 같은 책·장 사이에서 한 번 클릭으로 전환할 수 있게 만들었다.

| 버전 | 슬러그 | 분량 | 톤 |
|------|------|------|----|
| **21세기 성경** 📖 | `/<book>/<n>` | 1,363장 | 평어, 짧은 문장, 한자어 풀이, 부연 인용 |
| **어린이 성경** 🌱 | `/kidsb/<book>/<n>` | 1,335장 | 8–10세 어미(`~답니다/~었어요`), 의성어, 호기심 자극형 부연 |
| **개역한글** 📜 | `/krv/<book>/<n>` | 1,189장 | 1961년 개역한글판 원문 (Public Domain, 대한성서공회) |
| **외경 9권** ✦ | 위 3개에 통합 | 146장 | 한국 천주교 새번역 표기 (krv 미수록) |

빌드 결과: 정적 HTML **약 4,100페이지**.

---

## 주요 기능

- **3-way 본문 토글** — 모든 페이지 상단 picker로 같은 책·장의 다른 버전 즉시 이동.
- **장별 picker** — 책 목차를 누르지 않고 다른 장으로 점프.
- **인쇄용 CSS** — 브라우저 `Cmd+P` → "PDF로 저장"이 그대로 깔끔.
- **책 단위 PDF 빌더** — `python3 build/build_pdf_book.py 룻기` 한 줄로 책 한 권 PDF.
- **사이트맵·OG 태그·JSON-LD** — SEO 기본 항목 포함.
- **GitHub Pages 자동 배포** — `main`에 push하면 Astro 빌드 → Pages.

---

## 프로젝트 구조

```
.
├── 창세기/, 출애굽기/, …          # 21세기 성경 본문 (한국어 디렉토리, 마크다운)
├── 토빗기/, 유딧기/, …            # 외경 9권 (한국 천주교 새번역 표기)
├── 통합복음서/                    # 21cb 부록 — 4복음서 합본
├── kidsb/<책>/                    # 어린이판 본문 (같은 책 구조)
├── astro/
│   ├── src/
│   │   ├── content/<slug>/        # 빌드용 마크다운 (frontmatter + <sup> 변환)
│   │   ├── content/kidsb-<slug>/  # 어린이판 빌드 콘텐츠
│   │   ├── content/krv-<slug>/    # 개역한글 빌드 콘텐츠
│   │   ├── pages/<slug>/          # 동적 라우트 [chapter].astro
│   │   ├── layouts/               # Reader / KidsReader / KrvReader
│   │   ├── components/            # Breadcrumb 변형 3종
│   │   └── styles/                # global.css + kidsb.css
│   └── astro.config.mjs
├── build/
│   ├── migrate_to_astro.py        # 21cb 어른용 마크다운 → astro content
│   ├── sync_kidsb_to_astro.py     # 어린이판 동기화
│   ├── build_krv_to_astro.py      # 개역한글 JSON → astro content
│   ├── build_pdf_book.py          # 책별 PDF 생성 (pandoc + weasyprint)
│   └── build_epub.py              # EPUB 생성
├── EDITING_PRINCIPLES.md          # 어른용 본문 편집 원칙
└── kidsb/EDITING_PRINCIPLES.md    # 어린이판 편집 원칙
```

본문 마크다운은 사람이 읽기 좋은 형식으로 작성한 후, 빌드 스크립트가 Astro 콘텐츠 컬렉션 형식(`<sup class="verse">`, frontmatter 등)으로 변환한다.

---

## 로컬 개발

### 사전 요구 사항

- **Node.js 22+** (Astro 6.x)
- **Python 3.10+** (빌드 스크립트)
- **pandoc** + **weasyprint** (PDF 생성, 선택)

### 설치 + 개발 서버

```sh
cd astro
npm install
npm run dev
# http://localhost:4321/21cb
```

### 본문 추가/수정 후 동기화

본문은 root의 한국어 디렉토리(`창세기/01장.md` 등)에 작성하고, 빌드 스크립트로 astro 콘텐츠로 옮긴다:

```sh
# 21세기 성경 어른용
python3 build/migrate_to_astro.py

# 어린이 성경
python3 build/sync_kidsb_to_astro.py

# 개역한글 (외부 데이터셋 clone 후 1회)
git clone https://github.com/bluesaurel/Korean-Bible-1961-KRV /tmp/Korean-Bible-1961-KRV
python3 build/build_krv_to_astro.py
```

### 정적 사이트 빌드

```sh
cd astro
npm run build      # → astro/dist/
npm run preview    # 빌드 결과 미리보기
```

### 책별 PDF 생성

```sh
python3 build/build_pdf_book.py 창세기              # 전권
python3 build/build_pdf_book.py 마태복음 5 7        # 5–7장만
# → build/<책>_전권.pdf
```

---

## 배포

- **GitHub Pages**: `main` 브랜치 push 시 `.github/workflows/deploy.yml`이 자동으로 Astro 빌드 → Pages 배포.
- **사이트 base path**: `/21cb` (커스텀 도메인이 아니므로 `astro.config.mjs`의 `base` 사용).

수동 배포가 필요하면:

```sh
gh workflow run deploy.yml
```

---

## 본문 편집 원칙

- 어른용: [`EDITING_PRINCIPLES.md`](EDITING_PRINCIPLES.md)
- 어린이판: [`kidsb/EDITING_PRINCIPLES.md`](kidsb/EDITING_PRINCIPLES.md)

어른용 톤은 *현대 한국어 + 중학생 가독성 + 한자어·수사 군더더기 최소화*. 어린이판은 *8–10세 어미 + 의성어·의태어 + 호기심 자극형 부연*.

---

## 데이터 출처 / 라이선스

| 자원 | 출처 | 라이선스 |
|------|------|----------|
| **21세기 성경** (어른용 본문) | 본 프로젝트 새 번역 | CC BY-SA 4.0 |
| **어린이 성경** | 본 프로젝트 새 작성 | CC BY-SA 4.0 |
| **개역한글 (1961)** | [bluesaurel/Korean-Bible-1961-KRV](https://github.com/bluesaurel/Korean-Bible-1961-KRV) | Public Domain (저작자 표시: 대한성서공회) |
| **외경 9권** (천주교 정경) | 본 프로젝트 새 번역, 한국 천주교 새번역 표기 따름 | CC BY-SA 4.0 |
| **소스 코드** (Astro/Python) | 본 프로젝트 | MIT |

- 콘텐츠(번역본): [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — 출처 표시 + 동일 조건으로 자유 공유.
- 코드: [MIT](LICENSE) — 자유 사용·수정·재배포.
- 개역한글은 1961년판으로 저작재산권 보호기간 만료(50년+). 사용 시 *대한성서공회* 저작자 표시 의무. 출처: [BSK 공지](https://www.bskorea.or.kr/bbs/board.php?bo_table=copyright_faq&wr_id=5).
- 한국 천주교 새번역(2005)·공동번역(1977)·개역개정(1998) 같은 다른 번역본은 **사용하지 않음** (저작권 보호 중).

---

## 기여

이슈/PR 환영. 본문 수정 PR을 보낼 때:

1. root의 한국어 디렉토리(`창세기/01장.md` 등) 또는 `kidsb/<책>/<장>.md`만 편집.
2. 해당 빌드 스크립트(`migrate_to_astro.py` / `sync_kidsb_to_astro.py`) 실행 후 변경 결과 확인.
3. 편집 원칙(`EDITING_PRINCIPLES.md`) 준수.

번역 자체에 의견이 있으면 GitHub Issue로 — 어떤 책·장·절인지 구체적으로.

---

## 감사

- **대한성서공회** — 1961년 개역한글판 본문.
- **[bluesaurel/Korean-Bible-1961-KRV](https://github.com/bluesaurel/Korean-Bible-1961-KRV)** — 검증된 KRV JSON 데이터셋.
- **[Astro](https://astro.build/)** — 정적 사이트 프레임워크.
- **WeasyPrint, Pandoc** — PDF 빌드 파이프라인.

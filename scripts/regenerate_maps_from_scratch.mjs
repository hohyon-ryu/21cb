import fs from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const ROOT = "/Users/will/workspace/bible/site";
const OUT_DIR = path.join(ROOT, "assets/maps/genesis");

const mapBasePromptCommon =
  "ancient parchment cartography style map, levant and mesopotamia geography, coastlines, rivers, mountains, topographic hand-drawn look, ultra detailed, no labels, no text, no title, no border text";

const entries = [
  {
    file: "01_eden_and_four_rivers.png",
    seedMap: 501,
    seedPhoto: 1501,
    mapPrompt: `${mapBasePromptCommon}, eden region symbolic oasis near major rivers, broad levant and persian gulf view`,
    photoPrompt:
      "photorealistic lush river garden at dawn in ancient mesopotamia, mist, soft sun rays, no text",
    photoArea: { x: 960, y: 690, w: 520, h: 270 },
    labels: [
      { text: "에덴 / Eden", x: 690, y: 430, size: 32 },
      { text: "티그리스 / Tigris", x: 910, y: 300, size: 25 },
      { text: "유프라테스 / Euphrates", x: 880, y: 560, size: 25 },
      { text: "가나안 / Canaan", x: 300, y: 710, size: 25 }
    ]
  },
  {
    file: "02_east_of_eden_and_nod.png",
    seedMap: 502,
    seedPhoto: 1502,
    mapPrompt: `${mapBasePromptCommon}, eastward corridor from eden toward nod, mesopotamia and arabian frontier`,
    photoPrompt:
      "photorealistic ancient near east exile journey crossing dry uplands, cinematic, no text",
    photoArea: { x: 960, y: 680, w: 520, h: 280 },
    labels: [
      { text: "에덴 / Eden", x: 690, y: 435, size: 32 },
      { text: "놋 땅 / Land of Nod", x: 1035, y: 530, size: 30 },
      { text: "동쪽 이동 / Eastward Route", x: 800, y: 500, size: 24 }
    ],
    routePath: "M 760 460 C 900 450, 1030 470, 1210 520"
  },
  {
    file: "03_flood_to_ararat.png",
    seedMap: 503,
    seedPhoto: 1503,
    mapPrompt: `${mapBasePromptCommon}, northern high mountains of ararat after great flood, flood basin geography`,
    photoPrompt:
      "photorealistic high mountains after catastrophic flood with receding waters, dramatic clouds, no text",
    photoArea: { x: 850, y: 90, w: 620, h: 320 },
    labels: [
      { text: "아라랏 / Ararat", x: 930, y: 260, size: 31 },
      { text: "홍수 범람지 / Flooded Region", x: 590, y: 640, size: 25 },
      { text: "정착 지점 / Landing", x: 970, y: 350, size: 24 }
    ]
  },
  {
    file: "04_babel_and_dispersion.png",
    seedMap: 504,
    seedPhoto: 1504,
    mapPrompt: `${mapBasePromptCommon}, shinar plain and babel region, routes spreading to surrounding lands`,
    photoPrompt:
      "photorealistic ancient mesopotamian city under tower construction, workers and bricks, no text",
    photoArea: { x: 930, y: 640, w: 560, h: 300 },
    labels: [
      { text: "바벨 / Babel", x: 900, y: 520, size: 31 },
      { text: "시날 / Shinar", x: 1035, y: 570, size: 24 },
      { text: "확산 / Dispersion", x: 690, y: 320, size: 24 }
    ],
    routePath: "M 890 500 C 760 430, 670 350, 610 270"
  },
  {
    file: "05_abram_first_journey.png",
    seedMap: 505,
    seedPhoto: 1505,
    mapPrompt: `${mapBasePromptCommon}, ur to haran to canaan route panorama, ancient caravan corridors`,
    photoPrompt:
      "photorealistic bronze age caravan with donkeys and tents on semi-arid trail, no text",
    photoArea: { x: 980, y: 100, w: 500, h: 280 },
    labels: [
      { text: "우르 / Ur", x: 1080, y: 710, size: 26 },
      { text: "하란 / Haran", x: 860, y: 360, size: 26 },
      { text: "가나안 / Canaan", x: 510, y: 530, size: 26 },
      { text: "애굽 / Egypt", x: 260, y: 790, size: 26 }
    ],
    routePath: "M 1060 690 C 930 560, 890 420, 760 360 C 650 420, 560 490, 500 520"
  },
  {
    file: "06_kings_war_and_promise_land.png",
    seedMap: 506,
    seedPhoto: 1506,
    mapPrompt: `${mapBasePromptCommon}, transjordan and canaan war theater geography, strategic routes and valleys`,
    photoPrompt:
      "photorealistic bronze age battle movement in near east valley, dust and formations, no text",
    photoArea: { x: 900, y: 700, w: 580, h: 280 },
    labels: [
      { text: "전쟁 동선 / War Route", x: 830, y: 380, size: 24 },
      { text: "약속의 땅 / Promised Land", x: 1115, y: 620, size: 24 },
      { text: "헤브론 / Hebron", x: 430, y: 780, size: 27 }
    ],
    routePath: "M 1110 610 C 980 530, 900 460, 820 390 C 710 460, 630 610, 500 770"
  },
  {
    file: "07_patriarch_centers_hebron_beersheba_moriah.png",
    seedMap: 507,
    seedPhoto: 1507,
    mapPrompt: `${mapBasePromptCommon}, patriarchal centers in canaan highlands, hebron beersheba moriah triangle`,
    photoPrompt:
      "photorealistic ancient pastoral camp with stone altar in hill country, early morning, no text",
    photoArea: { x: 940, y: 90, w: 540, h: 280 },
    labels: [
      { text: "헤브론 / Hebron", x: 560, y: 620, size: 27 },
      { text: "브엘세바 / Beersheba", x: 470, y: 745, size: 26 },
      { text: "모리아 / Moriah", x: 650, y: 455, size: 26 }
    ],
    routePath: "M 580 610 C 590 550, 620 500, 655 465 C 610 530, 560 630, 485 735"
  },
  {
    file: "08_rebekah_route_aram_to_canaan.png",
    seedMap: 508,
    seedPhoto: 1508,
    mapPrompt: `${mapBasePromptCommon}, aram to canaan long-distance route across fertile crescent`,
    photoPrompt:
      "photorealistic family caravan with camels moving from aram to canaan, no text",
    photoArea: { x: 930, y: 650, w: 560, h: 310 },
    labels: [
      { text: "아람 / Aram", x: 930, y: 300, size: 27 },
      { text: "가나안 / Canaan", x: 500, y: 560, size: 27 },
      { text: "이동 경로 / Route", x: 750, y: 480, size: 24 }
    ],
    routePath: "M 930 310 C 860 380, 800 430, 750 470 C 650 520, 560 550, 510 555"
  },
  {
    file: "09_jacob_flight_and_return.png",
    seedMap: 509,
    seedPhoto: 1509,
    mapPrompt: `${mapBasePromptCommon}, jacob flight and return corridor, jabbok crossing terrain`,
    photoPrompt:
      "photorealistic lone traveler and small caravan on rugged valley route at dusk, no text",
    photoArea: { x: 930, y: 100, w: 560, h: 300 },
    labels: [
      { text: "도주 / Flight", x: 860, y: 400, size: 25 },
      { text: "귀환 / Return", x: 745, y: 650, size: 25 },
      { text: "얍복 / Jabbok", x: 670, y: 530, size: 24 }
    ],
    routePath: "M 870 390 C 780 450, 720 520, 690 530 C 710 580, 730 620, 760 640"
  },
  {
    file: "10_shechem_bethel_seir.png",
    seedMap: 510,
    seedPhoto: 1510,
    mapPrompt: `${mapBasePromptCommon}, shechem bethel seir sphere, canaan highlands to edom`,
    photoPrompt:
      "photorealistic hill-country settlement with shepherds and stone homes in ancient canaan, no text",
    photoArea: { x: 900, y: 660, w: 580, h: 300 },
    labels: [
      { text: "세겜 / Shechem", x: 580, y: 440, size: 26 },
      { text: "벧엘 / Bethel", x: 650, y: 515, size: 26 },
      { text: "세일 / Seir", x: 900, y: 680, size: 26 }
    ],
    routePath: "M 595 435 C 620 470, 640 500, 665 510 C 760 580, 830 640, 910 670"
  },
  {
    file: "11_joseph_route_to_egypt.png",
    seedMap: 511,
    seedPhoto: 1511,
    mapPrompt: `${mapBasePromptCommon}, canaan to egypt transfer route with nile delta geography`,
    photoPrompt:
      "photorealistic caravan transporting captive toward egyptian delta, ancient near east, no text",
    photoArea: { x: 850, y: 680, w: 620, h: 300 },
    labels: [
      { text: "가나안 / Canaan", x: 680, y: 370, size: 29 },
      { text: "애굽 / Egypt", x: 420, y: 770, size: 31 },
      { text: "이동 동선 / Transfer Route", x: 630, y: 530, size: 24 }
    ],
    routePath: "M 820 510 C 740 520, 660 540, 600 580 C 520 640, 470 710, 440 760"
  },
  {
    file: "12_famine_trips_canaan_egypt.png",
    seedMap: 512,
    seedPhoto: 1512,
    mapPrompt: `${mapBasePromptCommon}, repeated famine journeys between canaan and egypt, nile and levant corridor`,
    photoPrompt:
      "photorealistic ancient grain market and famine-era travelers in egypt, no text",
    photoArea: { x: 830, y: 680, w: 620, h: 300 },
    labels: [
      { text: "가나안 / Canaan", x: 740, y: 380, size: 28 },
      { text: "애굽 / Egypt", x: 480, y: 770, size: 30 },
      { text: "왕복 동선 / Round Trip", x: 655, y: 540, size: 24 }
    ],
    routePath: "M 770 520 C 680 540, 610 580, 530 650 C 500 690, 485 730, 500 770 M 500 770 C 550 690, 610 640, 700 590 C 745 560, 760 540, 770 520"
  },
  {
    file: "13_jacob_funeral_procession.png",
    seedMap: 513,
    seedPhoto: 1513,
    mapPrompt: `${mapBasePromptCommon}, egypt to hebron funeral procession route across sinai corridor`,
    photoPrompt:
      "photorealistic ancient funeral procession crossing desert corridor with chariots and mourners, no text",
    photoArea: { x: 860, y: 710, w: 630, h: 260 },
    labels: [
      { text: "고센 / Goshen", x: 210, y: 500, size: 30 },
      { text: "헤브론 / Hebron", x: 1120, y: 270, size: 28 },
      { text: "장례 행렬 / Procession", x: 720, y: 560, size: 24 }
    ],
    routePath: "M 285 575 C 430 560, 590 660, 760 640 C 900 620, 1030 500, 1130 300"
  }
];

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const esc = (s) =>
  s
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");

async function fetchImage(prompt, seed, kind) {
  const encoded = encodeURIComponent(prompt);
  const url = `https://image.pollinations.ai/prompt/${encoded}?width=1536&height=1024&seed=${seed}&nologo=true&enhance=true`;

  for (let attempt = 1; attempt <= 9; attempt += 1) {
    try {
      const res = await fetch(url, { headers: { Accept: "image/*" } });
      if (res.ok) {
        const buf = Buffer.from(await res.arrayBuffer());
        if (buf.byteLength > 10000) {
          return buf;
        }
      }
      if (res.status !== 429 && res.status < 500) {
        throw new Error(`${kind} generation failed with status ${res.status}`);
      }
    } catch (err) {
      if (attempt === 9) {
        throw err;
      }
    }

    await sleep(3500 * attempt);
  }

  throw new Error(`${kind} generation exhausted retries`);
}

function buildLabelSvg(width, height, labels, routePath) {
  const parts = [];

  if (routePath) {
    parts.push(
      `<path d="${esc(routePath)}" fill="none" stroke="rgba(118,55,30,0.88)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" />`
    );
    parts.push(
      `<path d="${esc(routePath)}" fill="none" stroke="rgba(244,220,186,0.28)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />`
    );
  }

  for (const l of labels) {
    parts.push(
      `<text x="${l.x + 1}" y="${l.y + 1}" fill="rgba(244,229,198,0.88)" font-family="Apple SD Gothic Neo, Noto Sans KR, sans-serif" font-size="${l.size}" font-weight="800">${esc(l.text)}</text>`
    );
    parts.push(
      `<text x="${l.x}" y="${l.y}" fill="#2b2219" stroke="rgba(236,220,188,0.60)" stroke-width="1.15" paint-order="stroke fill" font-family="Apple SD Gothic Neo, Noto Sans KR, sans-serif" font-size="${l.size}" font-weight="800">${esc(l.text)}</text>`
    );
  }

  return Buffer.from(
    `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">${parts.join("\n")}</svg>`
  );
}

function buildFeatherMask(w, h) {
  return Buffer.from(`
<svg width="${w}" height="${h}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="fade" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="white" />
      <stop offset="60%" stop-color="white" />
      <stop offset="84%" stop-color="rgba(255,255,255,0.25)" />
      <stop offset="100%" stop-color="rgba(255,255,255,0)" />
    </radialGradient>
  </defs>
  <ellipse cx="${Math.round(w / 2)}" cy="${Math.round(h / 2)}" rx="${Math.round(w * 0.48)}" ry="${Math.round(h * 0.46)}" fill="url(#fade)" />
</svg>`);
}

await fs.mkdir(OUT_DIR, { recursive: true });

for (let i = 0; i < entries.length; i += 1) {
  const e = entries[i];
  const outPath = path.join(OUT_DIR, e.file);

  console.log(`regen ${e.file} (${i + 1}/${entries.length})`);

  await sleep(2500);
  const mapBuf = await fetchImage(e.mapPrompt, e.seedMap, `map ${e.file}`);
  await sleep(2500);
  const photoBuf = await fetchImage(e.photoPrompt, e.seedPhoto, `photo ${e.file}`);

  const width = 1536;
  const height = 1024;

  const mapBase = await sharp(mapBuf)
    .resize(width, height, { fit: "cover" })
    .modulate({ saturation: 0.9, brightness: 0.98 })
    .png()
    .toBuffer();

  const area = e.photoArea;
  const photoPatch = await sharp(photoBuf)
    .resize(area.w, area.h, { fit: "cover" })
    .modulate({ saturation: 0.95, brightness: 0.93 })
    .ensureAlpha(0.76)
    .png()
    .toBuffer();

  const maskedPatch = await sharp(photoPatch)
    .composite([{ input: buildFeatherMask(area.w, area.h), blend: "dest-in" }])
    .png()
    .toBuffer();

  const composed = await sharp(mapBase)
    .composite([
      { input: maskedPatch, left: area.x, top: area.y, blend: "soft-light" },
      { input: buildLabelSvg(width, height, e.labels, e.routePath) }
    ])
    .png({ compressionLevel: 9 })
    .toBuffer();

  await fs.writeFile(outPath, composed);
}

console.log("ALL_MAPS_REGENERATED", entries.length);

import fs from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const ROOT = "/Users/will/workspace/bible/site";
const OUT_DIR = path.join(ROOT, "assets/maps/genesis");
const CACHE_DIR = path.join(ROOT, ".tile-cache-opentopo");
const TILE_SIZE = 256;
const WIDTH = 1536;
const HEIGHT = 1024;

const entries = [
  {
    file: "01_eden_and_four_rivers.png",
    center: { lat: 33.3, lon: 42.7 },
    zoom: 5,
    photoPrompt:
      "photorealistic lush river garden at dawn in ancient mesopotamia, mist, soft sun rays, no text",
    photoSeed: 7101,
    photoCenter: { lat: 31.5, lon: 45.8 },
    photoSize: { w: 520, h: 280 },
    labels: [
      { text: "에덴 / Eden", lat: 33.1, lon: 44.0, size: 33 },
      { text: "티그리스 / Tigris", lat: 35.7, lon: 43.3, size: 25 },
      { text: "유프라테스 / Euphrates", lat: 33.0, lon: 43.1, size: 25 },
      { text: "가나안 / Canaan", lat: 31.5, lon: 35.3, size: 25 }
    ]
  },
  {
    file: "02_east_of_eden_and_nod.png",
    center: { lat: 33.1, lon: 43.8 },
    zoom: 5,
    photoPrompt:
      "photorealistic ancient near east exile journey crossing dry highlands, cinematic realism, no text",
    photoSeed: 7102,
    photoCenter: { lat: 31.4, lon: 46.3 },
    photoSize: { w: 520, h: 290 },
    labels: [
      { text: "에덴 / Eden", lat: 33.1, lon: 44.0, size: 33 },
      { text: "놋 땅 / Land of Nod", lat: 32.5, lon: 47.3, size: 29 },
      { text: "동쪽 이동 / Eastward Route", lat: 32.8, lon: 45.8, size: 23 }
    ],
    routes: [
      [
        { lat: 33.1, lon: 44.0 },
        { lat: 32.9, lon: 45.0 },
        { lat: 32.7, lon: 46.0 },
        { lat: 32.5, lon: 47.3 }
      ]
    ]
  },
  {
    file: "03_flood_to_ararat.png",
    center: { lat: 38.6, lon: 43.8 },
    zoom: 5,
    photoPrompt:
      "photorealistic high mountains after catastrophic flood with receding waters and heavy clouds, no text",
    photoSeed: 7103,
    photoCenter: { lat: 39.5, lon: 44.2 },
    photoSize: { w: 620, h: 310 },
    labels: [
      { text: "아라랏 / Ararat", lat: 39.7, lon: 44.3, size: 31 },
      { text: "홍수 범람지 / Flooded Region", lat: 36.3, lon: 41.5, size: 23 },
      { text: "정착 지점 / Landing", lat: 39.4, lon: 44.0, size: 22 }
    ]
  },
  {
    file: "04_babel_and_dispersion.png",
    center: { lat: 33.0, lon: 44.4 },
    zoom: 5,
    photoPrompt:
      "photorealistic ancient mesopotamian city under monumental tower construction, no text",
    photoSeed: 7104,
    photoCenter: { lat: 32.6, lon: 44.5 },
    photoSize: { w: 560, h: 300 },
    labels: [
      { text: "바벨 / Babel", lat: 32.55, lon: 44.42, size: 31 },
      { text: "시날 / Shinar", lat: 32.8, lon: 45.2, size: 23 },
      { text: "확산 / Dispersion", lat: 34.4, lon: 42.0, size: 23 }
    ],
    routes: [
      [
        { lat: 32.55, lon: 44.42 },
        { lat: 33.2, lon: 43.7 },
        { lat: 34.0, lon: 42.8 },
        { lat: 34.6, lon: 41.9 }
      ]
    ]
  },
  {
    file: "05_abram_first_journey.png",
    center: { lat: 33.0, lon: 39.5 },
    zoom: 4,
    photoPrompt:
      "photorealistic bronze age caravan with tents and donkeys on long desert route, no text",
    photoSeed: 7105,
    photoCenter: { lat: 35.7, lon: 40.6 },
    photoSize: { w: 520, h: 290 },
    labels: [
      { text: "우르 / Ur", lat: 30.96, lon: 46.10, size: 25 },
      { text: "하란 / Haran", lat: 36.87, lon: 39.03, size: 25 },
      { text: "가나안 / Canaan", lat: 31.7, lon: 35.2, size: 25 },
      { text: "애굽 / Egypt", lat: 30.9, lon: 31.3, size: 25 }
    ],
    routes: [
      [
        { lat: 30.96, lon: 46.10 },
        { lat: 34.0, lon: 42.0 },
        { lat: 36.87, lon: 39.03 },
        { lat: 34.5, lon: 37.0 },
        { lat: 31.7, lon: 35.2 },
        { lat: 30.9, lon: 31.3 }
      ]
    ]
  },
  {
    file: "06_kings_war_and_promise_land.png",
    center: { lat: 33.0, lon: 38.6 },
    zoom: 5,
    photoPrompt:
      "photorealistic bronze age battlefield movement in near east valley terrain, dust and formations, no text",
    photoSeed: 7106,
    photoCenter: { lat: 31.8, lon: 40.0 },
    photoSize: { w: 580, h: 280 },
    labels: [
      { text: "전쟁 동선 / War Route", lat: 33.6, lon: 39.7, size: 22 },
      { text: "약속의 땅 / Promised Land", lat: 31.2, lon: 35.7, size: 22 },
      { text: "헤브론 / Hebron", lat: 31.53, lon: 35.10, size: 25 }
    ],
    routes: [
      [
        { lat: 34.6, lon: 43.0 },
        { lat: 33.8, lon: 40.8 },
        { lat: 32.8, lon: 39.5 },
        { lat: 31.53, lon: 35.10 }
      ]
    ]
  },
  {
    file: "07_patriarch_centers_hebron_beersheba_moriah.png",
    center: { lat: 31.6, lon: 35.3 },
    zoom: 7,
    photoPrompt:
      "photorealistic ancient pastoral camp with stone altar in canaan highlands, no text",
    photoSeed: 7107,
    photoCenter: { lat: 31.45, lon: 35.05 },
    photoSize: { w: 530, h: 280 },
    labels: [
      { text: "헤브론 / Hebron", lat: 31.53, lon: 35.10, size: 24 },
      { text: "브엘세바 / Beersheba", lat: 31.25, lon: 34.79, size: 23 },
      { text: "모리아 / Moriah", lat: 31.78, lon: 35.23, size: 23 }
    ],
    routes: [
      [
        { lat: 31.53, lon: 35.10 },
        { lat: 31.64, lon: 35.16 },
        { lat: 31.78, lon: 35.23 },
        { lat: 31.52, lon: 35.00 },
        { lat: 31.25, lon: 34.79 }
      ]
    ]
  },
  {
    file: "08_rebekah_route_aram_to_canaan.png",
    center: { lat: 34.4, lon: 38.9 },
    zoom: 5,
    photoPrompt:
      "photorealistic ancient family caravan with camels crossing fertile crescent route, no text",
    photoSeed: 7108,
    photoCenter: { lat: 34.0, lon: 39.8 },
    photoSize: { w: 560, h: 300 },
    labels: [
      { text: "아람 / Aram", lat: 35.5, lon: 40.0, size: 25 },
      { text: "가나안 / Canaan", lat: 31.8, lon: 35.2, size: 25 },
      { text: "이동 경로 / Route", lat: 33.5, lon: 37.8, size: 22 }
    ],
    routes: [
      [
        { lat: 35.5, lon: 40.0 },
        { lat: 34.7, lon: 39.0 },
        { lat: 33.6, lon: 37.9 },
        { lat: 32.8, lon: 36.5 },
        { lat: 31.8, lon: 35.2 }
      ]
    ]
  },
  {
    file: "09_jacob_flight_and_return.png",
    center: { lat: 33.1, lon: 37.8 },
    zoom: 6,
    photoPrompt:
      "photorealistic lone traveler and small caravan on rugged valley crossing at dusk, no text",
    photoSeed: 7109,
    photoCenter: { lat: 33.0, lon: 38.6 },
    photoSize: { w: 560, h: 280 },
    labels: [
      { text: "도주 / Flight", lat: 33.3, lon: 38.8, size: 23 },
      { text: "귀환 / Return", lat: 32.3, lon: 35.8, size: 23 },
      { text: "얍복 / Jabbok", lat: 32.2, lon: 35.9, size: 22 }
    ],
    routes: [
      [
        { lat: 31.8, lon: 35.2 },
        { lat: 32.8, lon: 37.0 },
        { lat: 33.4, lon: 39.2 }
      ],
      [
        { lat: 33.4, lon: 39.2 },
        { lat: 32.7, lon: 37.4 },
        { lat: 32.2, lon: 35.9 }
      ]
    ]
  },
  {
    file: "10_shechem_bethel_seir.png",
    center: { lat: 31.3, lon: 35.6 },
    zoom: 7,
    photoPrompt:
      "photorealistic ancient hill-country settlement with shepherd families and stone houses, no text",
    photoSeed: 7110,
    photoCenter: { lat: 30.7, lon: 35.8 },
    photoSize: { w: 560, h: 300 },
    labels: [
      { text: "세겜 / Shechem", lat: 32.22, lon: 35.26, size: 24 },
      { text: "벧엘 / Bethel", lat: 31.93, lon: 35.22, size: 24 },
      { text: "세일 / Seir", lat: 30.9, lon: 35.8, size: 24 }
    ],
    routes: [
      [
        { lat: 32.22, lon: 35.26 },
        { lat: 31.93, lon: 35.22 },
        { lat: 31.3, lon: 35.4 },
        { lat: 30.9, lon: 35.8 }
      ]
    ]
  },
  {
    file: "11_joseph_route_to_egypt.png",
    center: { lat: 31.1, lon: 33.7 },
    zoom: 6,
    photoPrompt:
      "photorealistic ancient caravan transporting captive toward egyptian delta, no text",
    photoSeed: 7111,
    photoCenter: { lat: 30.4, lon: 32.0 },
    photoSize: { w: 620, h: 300 },
    labels: [
      { text: "가나안 / Canaan", lat: 31.9, lon: 35.2, size: 28 },
      { text: "애굽 / Egypt", lat: 30.9, lon: 31.2, size: 30 },
      { text: "이동 동선 / Transfer Route", lat: 31.4, lon: 33.6, size: 22 }
    ],
    routes: [
      [
        { lat: 31.95, lon: 35.2 },
        { lat: 31.5, lon: 34.4 },
        { lat: 31.2, lon: 33.8 },
        { lat: 31.0, lon: 32.9 },
        { lat: 30.9, lon: 31.2 }
      ]
    ]
  },
  {
    file: "12_famine_trips_canaan_egypt.png",
    center: { lat: 31.1, lon: 33.7 },
    zoom: 6,
    photoPrompt:
      "photorealistic ancient famine-era grain market in egypt with traveling families, no text",
    photoSeed: 7112,
    photoCenter: { lat: 30.5, lon: 31.8 },
    photoSize: { w: 620, h: 300 },
    labels: [
      { text: "가나안 / Canaan", lat: 31.9, lon: 35.2, size: 28 },
      { text: "애굽 / Egypt", lat: 30.9, lon: 31.2, size: 30 },
      { text: "왕복 동선 / Round Trip", lat: 31.4, lon: 33.5, size: 22 }
    ],
    routes: [
      [
        { lat: 31.9, lon: 35.2 },
        { lat: 31.4, lon: 34.0 },
        { lat: 31.0, lon: 32.9 },
        { lat: 30.9, lon: 31.2 }
      ],
      [
        { lat: 30.9, lon: 31.2 },
        { lat: 31.2, lon: 33.0 },
        { lat: 31.5, lon: 34.2 },
        { lat: 31.9, lon: 35.2 }
      ]
    ]
  },
  {
    file: "13_jacob_funeral_procession.png",
    center: { lat: 30.9, lon: 34.1 },
    zoom: 6,
    photoPrompt:
      "photorealistic ancient funeral procession crossing sinai corridor with chariots and mourners, no text",
    photoSeed: 7113,
    photoCenter: { lat: 30.2, lon: 33.8 },
    photoSize: { w: 620, h: 280 },
    labels: [
      { text: "고센 / Goshen", lat: 30.95, lon: 31.4, size: 29 },
      { text: "헤브론 / Hebron", lat: 31.53, lon: 35.10, size: 27 },
      { text: "장례 행렬 / Procession", lat: 31.15, lon: 33.8, size: 22 }
    ],
    routes: [
      [
        { lat: 30.95, lon: 31.4 },
        { lat: 30.95, lon: 32.4 },
        { lat: 31.05, lon: 33.3 },
        { lat: 31.2, lon: 34.2 },
        { lat: 31.53, lon: 35.10 }
      ]
    ]
  }
];

function mod(n, m) {
  return ((n % m) + m) % m;
}

function latLonToWorld(lat, lon, zoom) {
  const scale = TILE_SIZE * 2 ** zoom;
  const x = ((lon + 180) / 360) * scale;
  const sinLat = Math.sin((lat * Math.PI) / 180);
  const y =
    (0.5 - Math.log((1 + sinLat) / (1 - sinLat)) / (4 * Math.PI)) * scale;
  return { x, y };
}

function latLonToPixel(lat, lon, center, zoom, width, height) {
  const world = latLonToWorld(lat, lon, zoom);
  const centerWorld = latLonToWorld(center.lat, center.lon, zoom);
  return {
    x: world.x - centerWorld.x + width / 2,
    y: world.y - centerWorld.y + height / 2
  };
}

async function fetchWithRetry(url, kind) {
  for (let attempt = 1; attempt <= 8; attempt += 1) {
    try {
      const res = await fetch(url, { headers: { Accept: "image/*" } });
      if (res.ok) {
        const buf = Buffer.from(await res.arrayBuffer());
        if (buf.byteLength > 1000) {
          return buf;
        }
      }
      if (res.status !== 429 && res.status < 500) {
        throw new Error(`${kind} failed: ${res.status}`);
      }
    } catch (err) {
      if (attempt === 8) {
        throw err;
      }
    }
    await new Promise((r) => setTimeout(r, 1800 * attempt));
  }
  throw new Error(`${kind} exhausted`);
}

async function getTopoTile(z, x, y) {
  const max = 2 ** z;
  const xx = mod(x, max);
  if (y < 0 || y >= max) {
    return sharp({
      create: {
        width: TILE_SIZE,
        height: TILE_SIZE,
        channels: 4,
        background: { r: 240, g: 238, b: 230, alpha: 1 }
      }
    })
      .png()
      .toBuffer();
  }

  const cachePath = path.join(CACHE_DIR, `${z}_${xx}_${y}.png`);
  try {
    return await fs.readFile(cachePath);
  } catch {}

  const url = `https://tile.opentopomap.org/${z}/${xx}/${y}.png`;
  const buf = await fetchWithRetry(url, `tile z${z}/${xx}/${y}`);
  await fs.mkdir(CACHE_DIR, { recursive: true });
  await fs.writeFile(cachePath, buf);
  return buf;
}

async function buildRealMap(center, zoom, width, height) {
  const centerWorld = latLonToWorld(center.lat, center.lon, zoom);
  const topLeftX = centerWorld.x - width / 2;
  const topLeftY = centerWorld.y - height / 2;

  const startTileX = Math.floor(topLeftX / TILE_SIZE);
  const endTileX = Math.floor((topLeftX + width - 1) / TILE_SIZE);
  const startTileY = Math.floor(topLeftY / TILE_SIZE);
  const endTileY = Math.floor((topLeftY + height - 1) / TILE_SIZE);

  const composites = [];
  for (let ty = startTileY; ty <= endTileY; ty += 1) {
    for (let tx = startTileX; tx <= endTileX; tx += 1) {
      const tile = await getTopoTile(zoom, tx, ty);
      const left = Math.round(tx * TILE_SIZE - topLeftX);
      const top = Math.round(ty * TILE_SIZE - topLeftY);
      composites.push({ input: tile, left, top });
    }
  }

  const canvas = await sharp({
    create: {
      width,
      height,
      channels: 4,
      background: { r: 245, g: 242, b: 235, alpha: 1 }
    }
  })
    .composite(composites)
    .png()
    .toBuffer();

  const tint = await sharp({
    create: {
      width,
      height,
      channels: 4,
      background: { r: 216, g: 198, b: 160, alpha: 0.15 }
    }
  })
    .png()
    .toBuffer();

  return sharp(canvas)
    .modulate({ saturation: 0.72, brightness: 0.96 })
    .composite([{ input: tint, blend: "multiply" }])
    .png()
    .toBuffer();
}

function esc(str) {
  return str
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function buildOverlaySvg(cfg) {
  const parts = [];

  if (cfg.routes) {
    for (const route of cfg.routes) {
      const pts = route
        .map((p, idx) => {
          const px = latLonToPixel(
            p.lat,
            p.lon,
            cfg.center,
            cfg.zoom,
            WIDTH,
            HEIGHT
          );
          return `${idx === 0 ? "M" : "L"} ${px.x.toFixed(1)} ${px.y.toFixed(1)}`;
        })
        .join(" ");

      parts.push(
        `<path d="${pts}" fill="none" stroke="rgba(122,45,22,0.85)" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round" />`
      );
      parts.push(
        `<path d="${pts}" fill="none" stroke="rgba(248,222,186,0.32)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />`
      );
    }
  }

  for (const l of cfg.labels) {
    const p = latLonToPixel(l.lat, l.lon, cfg.center, cfg.zoom, WIDTH, HEIGHT);
    const x = p.x.toFixed(1);
    const y = p.y.toFixed(1);
    parts.push(
      `<text x="${x}" y="${y}" fill="rgba(247,232,203,0.88)" font-family="Apple SD Gothic Neo, Noto Sans KR, sans-serif" font-size="${l.size}" font-weight="800">${esc(l.text)}</text>`
    );
    parts.push(
      `<text x="${x}" y="${y}" fill="#231c15" stroke="rgba(239,223,193,0.62)" stroke-width="1.15" paint-order="stroke fill" font-family="Apple SD Gothic Neo, Noto Sans KR, sans-serif" font-size="${l.size}" font-weight="800">${esc(l.text)}</text>`
    );
  }

  return Buffer.from(
    `<svg width="${WIDTH}" height="${HEIGHT}" xmlns="http://www.w3.org/2000/svg">${parts.join("\n")}</svg>`
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

async function generatePhoto(prompt, seed) {
  const url = `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?width=1536&height=1024&seed=${seed}&nologo=true&enhance=true`;
  return fetchWithRetry(url, `photo seed ${seed}`);
}

await fs.mkdir(OUT_DIR, { recursive: true });
for (const f of await fs.readdir(OUT_DIR)) {
  if (f.endsWith(".png")) {
    await fs.unlink(path.join(OUT_DIR, f));
  }
}

for (let i = 0; i < entries.length; i += 1) {
  const cfg = entries[i];
  console.log(`regen ${cfg.file} (${i + 1}/${entries.length})`);

  const baseMap = await buildRealMap(cfg.center, cfg.zoom, WIDTH, HEIGHT);
  const photo = await generatePhoto(cfg.photoPrompt, cfg.photoSeed);

  const photoCenterPx = latLonToPixel(
    cfg.photoCenter.lat,
    cfg.photoCenter.lon,
    cfg.center,
    cfg.zoom,
    WIDTH,
    HEIGHT
  );

  const left = Math.round(photoCenterPx.x - cfg.photoSize.w / 2);
  const top = Math.round(photoCenterPx.y - cfg.photoSize.h / 2);

  const patch = await sharp(photo)
    .resize(cfg.photoSize.w, cfg.photoSize.h, { fit: "cover" })
    .modulate({ saturation: 0.95, brightness: 0.92 })
    .ensureAlpha(0.72)
    .png()
    .toBuffer();

  const maskedPatch = await sharp(patch)
    .composite([{ input: buildFeatherMask(cfg.photoSize.w, cfg.photoSize.h), blend: "dest-in" }])
    .png()
    .toBuffer();

  const final = await sharp(baseMap)
    .composite([
      { input: maskedPatch, left, top, blend: "soft-light" },
      { input: buildOverlaySvg(cfg) }
    ])
    .png({ compressionLevel: 9 })
    .toBuffer();

  await fs.writeFile(path.join(OUT_DIR, cfg.file), final);
}

console.log("ALL_REAL_MAPS_REGENERATED", entries.length);

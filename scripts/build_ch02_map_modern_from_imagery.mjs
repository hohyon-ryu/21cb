import fs from "node:fs/promises";
import sharp from "sharp";

const input = "/Users/will/workspace/bible/site/assets/maps/genesis/ch02_modern_imagery_raw.png";
const output = "/Users/will/workspace/bible/site/assets/maps/genesis/ch02_chapter_map_eden_modern_location.png";
const boundaryGeoJsonPath =
  "/Users/will/workspace/bible/site/assets/maps/genesis/ne_110m_admin_0_boundary_lines_land.geojson";

const geoBbox = {
  minLon: 30,
  maxLon: 56,
  minLat: 22,
  maxLat: 40
};

const { width, height } = await sharp(input).metadata();

if (!width || !height) {
  throw new Error("Invalid image metadata");
}

const boundaryGeo = JSON.parse(await fs.readFile(boundaryGeoJsonPath, "utf8"));

const projectPoint = ([lon, lat]) => {
  const x = ((lon - geoBbox.minLon) / (geoBbox.maxLon - geoBbox.minLon)) * width;
  const y = ((geoBbox.maxLat - lat) / (geoBbox.maxLat - geoBbox.minLat)) * height;
  return [x, y];
};

const bboxIntersects = (coords) => {
  let minLon = Infinity;
  let maxLon = -Infinity;
  let minLat = Infinity;
  let maxLat = -Infinity;

  for (const [lon, lat] of coords) {
    if (lon < minLon) minLon = lon;
    if (lon > maxLon) maxLon = lon;
    if (lat < minLat) minLat = lat;
    if (lat > maxLat) maxLat = lat;
  }

  return !(
    maxLon < geoBbox.minLon ||
    minLon > geoBbox.maxLon ||
    maxLat < geoBbox.minLat ||
    minLat > geoBbox.maxLat
  );
};

const lineToPath = (coords) => {
  if (!coords || coords.length < 2 || !bboxIntersects(coords)) {
    return "";
  }

  let d = "";
  for (let i = 0; i < coords.length; i += 1) {
    const [x, y] = projectPoint(coords[i]);
    d += i === 0 ? `M ${x.toFixed(2)} ${y.toFixed(2)}` : ` L ${x.toFixed(2)} ${y.toFixed(2)}`;
  }
  return d;
};

const boundaryPathParts = [];
for (const feature of boundaryGeo.features) {
  const geom = feature?.geometry;
  if (!geom) continue;
  if (geom.type === "LineString") {
    const d = lineToPath(geom.coordinates);
    if (d) boundaryPathParts.push(d);
  } else if (geom.type === "MultiLineString") {
    for (const line of geom.coordinates) {
      const d = lineToPath(line);
      if (d) boundaryPathParts.push(d);
    }
  }
}

const boundaryPathData = boundaryPathParts.join(" ");

const svg = `
<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="labelShadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="2.2" stdDeviation="2.2" flood-color="#000000" flood-opacity="0.75"/>
    </filter>
    <filter id="lineShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1.2" stdDeviation="1.1" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- Probable Eden region: southern Iraq near Persian Gulf -->
  <circle cx="931" cy="561" r="78" fill="none" stroke="#ffe08c" stroke-width="4" stroke-dasharray="10 8" opacity="0.95" filter="url(#lineShadow)"/>
  <circle cx="931" cy="561" r="5.5" fill="#ffe08c" opacity="0.95"/>

  <path d="M 1008 590 C 1065 630, 1125 652, 1215 690" fill="none" stroke="#ffe08c" stroke-width="3.2" opacity="0.95" filter="url(#lineShadow)"/>

  <text x="1153" y="730" font-size="33" font-weight="780"
        font-family="'Apple SD Gothic Neo','Noto Sans CJK KR','Malgun Gothic',sans-serif"
        fill="#fff2c1" filter="url(#labelShadow)">추정 권역: 현대 이라크 남부</text>
  <text x="1153" y="769" font-size="28" font-weight="700"
        font-family="'Apple SD Gothic Neo','Noto Sans CJK KR','Malgun Gothic',sans-serif"
        fill="#fff2c1" filter="url(#labelShadow)">페르시아만 인접 메소포타미아</text>
  <text x="1153" y="804" font-size="23" font-weight="600"
        font-family="'Apple SD Gothic Neo','Noto Sans CJK KR','Malgun Gothic',sans-serif"
        fill="#fff2c1" filter="url(#labelShadow)">Southern Iraq near the Persian Gulf</text>

  <!-- Core river/context labels -->
  <text x="886" y="388" font-size="27" font-weight="740"
        font-family="'Apple SD Gothic Neo','Noto Sans CJK KR','Malgun Gothic',sans-serif"
        fill="#f2f7ff" filter="url(#labelShadow)">티그리스 / Tigris</text>
  <text x="767" y="468" font-size="27" font-weight="740"
        font-family="'Apple SD Gothic Neo','Noto Sans CJK KR','Malgun Gothic',sans-serif"
        fill="#f2f7ff" filter="url(#labelShadow)">유프라테스 / Euphrates</text>
  <text x="861" y="539" font-size="30" font-weight="780"
        font-family="'Apple SD Gothic Neo','Noto Sans CJK KR','Malgun Gothic',sans-serif"
        fill="#fff2c1" filter="url(#labelShadow)">에덴(상징) / Eden (Symbolic)</text>
  <text x="1045" y="628" font-size="24" font-weight="680"
        font-family="'Apple SD Gothic Neo','Noto Sans CJK KR','Malgun Gothic',sans-serif"
        fill="#f2f7ff" filter="url(#labelShadow)">메소포타미아 / Mesopotamia</text>
</svg>
`;

const borderSvg = `
<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="borderShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0.5" stdDeviation="0.6" flood-color="#120b05" flood-opacity="0.65"/>
    </filter>
  </defs>
  <path d="${boundaryPathData}" fill="none" stroke="#f8e4b2" stroke-width="1.6"
        stroke-linejoin="round" stroke-linecap="round" opacity="0.72" filter="url(#borderShadow)"/>
  <path d="${boundaryPathData}" fill="none" stroke="#3a2811" stroke-width="0.7"
        stroke-linejoin="round" stroke-linecap="round" opacity="0.5"/>
</svg>
`;

const toneSvg = `
<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="vignette" cx="50%" cy="48%" r="66%">
      <stop offset="58%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#3a2a10" stop-opacity="0.22"/>
    </radialGradient>
  </defs>
  <rect width="100%" height="100%" fill="#b89458" fill-opacity="0.18"/>
  <rect width="100%" height="100%" fill="url(#vignette)"/>
</svg>
`;

const textureSvg = `
<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="paperNoise" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="19" result="n"/>
      <feColorMatrix in="n" type="matrix"
        values="0 0 0 0 0.72
                0 0 0 0 0.60
                0 0 0 0 0.40
                0 0 0 0.10 0"/>
    </filter>
  </defs>
  <rect width="100%" height="100%" filter="url(#paperNoise)" opacity="0.35"/>
</svg>
`;

await sharp(input)
  .modulate({ brightness: 0.985, saturation: 0.9 })
  .composite([
    { input: Buffer.from(toneSvg), blend: "multiply" },
    { input: Buffer.from(textureSvg), blend: "soft-light" },
    { input: Buffer.from(borderSvg), blend: "over" },
    { input: Buffer.from(svg), blend: "over" }
  ])
  .png({ compressionLevel: 9, adaptiveFiltering: true })
  .toFile(output);

console.log("CH02_MODERN_MAP_FINAL_DONE");

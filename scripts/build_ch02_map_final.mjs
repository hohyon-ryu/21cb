import fs from "node:fs/promises";
import sharp from "sharp";

const input = "/Users/will/workspace/bible/site/assets/maps/genesis/01_eden_and_four_rivers.png";
const output = "/Users/will/workspace/bible/site/assets/maps/genesis/ch02_chapter_map_eden_modern_location.png";

const { width, height } = await sharp(input).metadata();

if (!width || !height) {
  throw new Error("Invalid base image size");
}

const svg = `
<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1.5" stdDeviation="1.2" flood-color="#f3e2b8" flood-opacity="0.65"/>
    </filter>
  </defs>

  <!-- Probable Eden region marker near lower Mesopotamia / Persian Gulf -->
  <circle cx="842" cy="566" r="118" fill="none" stroke="#3a4f34" stroke-width="5" stroke-dasharray="13 9" opacity="0.92"/>
  <circle cx="842" cy="566" r="9" fill="#3a4f34" opacity="0.95"/>
  <path d="M 930 620 C 1010 680, 1095 712, 1168 738" fill="none" stroke="#3a4f34" stroke-width="4" opacity="0.92"/>

  <text x="980" y="784" font-size="34" font-weight="700"
        font-family="'Apple SD Gothic Neo','Noto Sans CJK KR','Malgun Gothic',sans-serif"
        fill="#2f2516" filter="url(#softShadow)">추정 권역: 현대 이라크 남부</text>
  <text x="980" y="824" font-size="30" font-weight="650"
        font-family="'Apple SD Gothic Neo','Noto Sans CJK KR','Malgun Gothic',sans-serif"
        fill="#2f2516" filter="url(#softShadow)">페르시아만 인접 메소포타미아</text>
  <text x="980" y="861" font-size="25" font-weight="520"
        font-family="'Apple SD Gothic Neo','Noto Sans CJK KR','Malgun Gothic',sans-serif"
        fill="#3b2e1d" filter="url(#softShadow)">Southern Iraq near the Persian Gulf</text>
</svg>
`;

const overlay = Buffer.from(svg);

await fs.mkdir("/Users/will/workspace/bible/site/assets/maps/genesis", { recursive: true });

await sharp(input)
  .composite([{ input: overlay, blend: "over" }])
  .png({ compressionLevel: 9, adaptiveFiltering: true })
  .toFile(output);

console.log("CH02_MAP_FINAL_BUILT");

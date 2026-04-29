import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(SCRIPT_DIR, '../..');
const RAW = path.join(ROOT, 'astro/public/assets/covers/_raw/kidsb.png');
const COVER_OUT = path.join(ROOT, 'astro/public/assets/covers/kidsb.jpg');
const OG_OUT = path.join(ROOT, 'astro/public/assets/og/kidsb-og.jpg');

const COVER_WIDTH = 1024;
const COVER_HEIGHT = 1448;
const OG_WIDTH = 1200;
const OG_HEIGHT = 630;

function overlaySvg({ width, height, variant }) {
  const isOg = variant === 'og';
  const title = '어린이 성경';
  const subtitle = '초등학생을 위한 쉬운 번역본';
  const scope = '구약 39권 + 신약 27권';

  if (isOg) {
    return Buffer.from(`
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <defs>
    <linearGradient id="shade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff4cf" stop-opacity="0.94"/>
      <stop offset="0.46" stop-color="#fff4cf" stop-opacity="0.78"/>
      <stop offset="1" stop-color="#fff4cf" stop-opacity="0.08"/>
    </linearGradient>
    <linearGradient id="sun" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.28"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#5c3d14" flood-opacity="0.24"/>
    </filter>
  </defs>
  <rect width="${width}" height="${height}" fill="url(#shade)"/>
  <rect width="${width}" height="${height}" fill="url(#sun)"/>
  <text x="78" y="178"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="94" font-weight="800"
    fill="#1e5d4f" filter="url(#shadow)">${title}</text>
  <line x1="82" y1="224" x2="404" y2="224" stroke="#ffb84d" stroke-width="6" stroke-linecap="round"/>
  <text x="82" y="300"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="42" font-weight="800"
    fill="#27324a" filter="url(#shadow)">${subtitle}</text>
  <text x="84" y="362"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="31" font-weight="700"
    fill="#48715f" opacity="0.95">${scope}</text>
</svg>`);
  }

  return Buffer.from(`
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <defs>
    <linearGradient id="topShade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff8db" stop-opacity="0.96"/>
      <stop offset="0.34" stop-color="#fff8db" stop-opacity="0.74"/>
      <stop offset="0.58" stop-color="#fff8db" stop-opacity="0.18"/>
      <stop offset="1" stop-color="#fff8db" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="bottomShade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1e5d4f" stop-opacity="0"/>
      <stop offset="0.46" stop-color="#1e5d4f" stop-opacity="0.22"/>
      <stop offset="1" stop-color="#1e5d4f" stop-opacity="0.54"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#5c3d14" flood-opacity="0.24"/>
    </filter>
  </defs>
  <rect width="${width}" height="520" fill="url(#topShade)"/>
  <rect y="870" width="${width}" height="578" fill="url(#bottomShade)"/>
  <text x="${width / 2}" y="170" text-anchor="middle"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="86" font-weight="800"
    fill="#1e5d4f" filter="url(#shadow)">${title}</text>
  <line x1="364" y1="218" x2="660" y2="218" stroke="#ffb84d" stroke-width="6" stroke-linecap="round"/>
  <text x="${width / 2}" y="288" text-anchor="middle"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="38" font-weight="800"
    fill="#27324a" filter="url(#shadow)">${subtitle}</text>
  <text x="${width / 2}" y="350" text-anchor="middle"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="30" font-weight="700"
    fill="#48715f" opacity="0.95">${scope}</text>
</svg>`);
}

async function buildCover() {
  await sharp(RAW)
    .resize(COVER_WIDTH, COVER_HEIGHT, { fit: 'cover', position: 'attention' })
    .modulate({ saturation: 1.02, brightness: 0.99 })
    .composite([{ input: overlaySvg({ width: COVER_WIDTH, height: COVER_HEIGHT, variant: 'cover' }) }])
    .withMetadata()
    .jpeg({ quality: 90, progressive: false })
    .toFile(COVER_OUT);
}

async function buildOg() {
  await sharp(RAW)
    .resize(OG_WIDTH, OG_HEIGHT, { fit: 'cover', position: 'attention' })
    .modulate({ saturation: 1.02, brightness: 0.98 })
    .composite([{ input: overlaySvg({ width: OG_WIDTH, height: OG_HEIGHT, variant: 'og' }) }])
    .withMetadata()
    .jpeg({ quality: 88, progressive: false })
    .toFile(OG_OUT);
}

await fs.mkdir(path.dirname(COVER_OUT), { recursive: true });
await fs.mkdir(path.dirname(OG_OUT), { recursive: true });
await buildCover();
await buildOg();

console.log(`cover: ${COVER_OUT}`);
console.log(`og: ${OG_OUT}`);

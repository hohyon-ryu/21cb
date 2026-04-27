import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(SCRIPT_DIR, '../..');
const RAW = path.join(ROOT, 'astro/public/assets/covers/_raw/full.png');
const COVER_OUT = path.join(ROOT, 'astro/public/assets/covers/full.jpg');
const OG_OUT = path.join(ROOT, 'astro/public/assets/og/21cb-og.jpg');

const COVER_WIDTH = 1024;
const COVER_HEIGHT = 1448;
const OG_WIDTH = 1200;
const OG_HEIGHT = 630;

function overlaySvg({ width, height, variant }) {
  const isOg = variant === 'og';
  const title = isOg ? '21세기 성경' : '21세기에 읽는 성경';
  const subtitle = '구약 39권 + 신약 27권 합본';
  const edition = '현대 번역본';

  if (isOg) {
    return Buffer.from(`
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <defs>
    <linearGradient id="shade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#07111e" stop-opacity="0.86"/>
      <stop offset="0.48" stop-color="#07111e" stop-opacity="0.58"/>
      <stop offset="1" stop-color="#07111e" stop-opacity="0.12"/>
    </linearGradient>
    <linearGradient id="bottom" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0.42"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>
  <rect width="${width}" height="${height}" fill="url(#shade)"/>
  <rect y="${height * 0.5}" width="${width}" height="${height * 0.5}" fill="url(#bottom)"/>
  <text x="88" y="190"
    font-family="Apple SD Gothic Neo, Noto Serif CJK KR, Nanum Myeongjo, serif"
    font-size="92" font-weight="800"
    fill="#fffaf0" filter="url(#shadow)">${title}</text>
  <line x1="92" y1="235" x2="470" y2="235" stroke="#f8d782" stroke-width="4" stroke-opacity="0.9"/>
  <text x="92" y="312"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="42" font-weight="700" letter-spacing="1"
    fill="#f8fafc" filter="url(#shadow)">${subtitle}</text>
  <text x="92" y="378"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="30" font-weight="600" letter-spacing="5"
    fill="#d9e4ef" opacity="0.9" filter="url(#shadow)">${edition}</text>
</svg>`);
  }

  return Buffer.from(`
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <defs>
    <linearGradient id="topShade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#06111f" stop-opacity="0.42"/>
      <stop offset="0.34" stop-color="#06111f" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="bottomShade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#020712" stop-opacity="0"/>
      <stop offset="0.4" stop-color="#020712" stop-opacity="0.64"/>
      <stop offset="1" stop-color="#020712" stop-opacity="0.92"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#000000" flood-opacity="0.56"/>
    </filter>
  </defs>
  <rect width="${width}" height="${height}" fill="url(#topShade)"/>
  <rect y="760" width="${width}" height="688" fill="url(#bottomShade)"/>
  <text x="${width / 2}" y="1032" text-anchor="middle"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="35" font-weight="700" letter-spacing="8"
    fill="#d9e4ef" opacity="0.94" filter="url(#shadow)">21세기 성경</text>
  <text x="${width / 2}" y="1146" text-anchor="middle"
    font-family="Apple SD Gothic Neo, Noto Serif CJK KR, Nanum Myeongjo, serif"
    font-size="78" font-weight="800"
    fill="#fffaf0" filter="url(#shadow)">${title}</text>
  <line x1="342" y1="1194" x2="682" y2="1194" stroke="#f8d782" stroke-opacity="0.88" stroke-width="3"/>
  <text x="${width / 2}" y="1266" text-anchor="middle"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="34" font-weight="700"
    fill="#f8fafc" opacity="0.94" filter="url(#shadow)">${subtitle}</text>
  <text x="${width / 2}" y="1334" text-anchor="middle"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="30" font-weight="600" letter-spacing="5"
    fill="#d9e4ef" opacity="0.86" filter="url(#shadow)">${edition}</text>
</svg>`);
}

async function buildCover() {
  await sharp(RAW)
    .resize(COVER_WIDTH, COVER_HEIGHT, { fit: 'cover', position: 'attention' })
    .modulate({ saturation: 0.94, brightness: 0.96 })
    .composite([{ input: overlaySvg({ width: COVER_WIDTH, height: COVER_HEIGHT, variant: 'cover' }) }])
    .withMetadata()
    .jpeg({ quality: 90, progressive: false })
    .toFile(COVER_OUT);
}

async function buildOg() {
  await sharp(RAW)
    .resize(OG_WIDTH, OG_HEIGHT, { fit: 'cover', position: 'attention' })
    .modulate({ saturation: 0.96, brightness: 0.92 })
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

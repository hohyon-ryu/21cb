import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';

const ROOT = '/Users/will/workspace/bible';
const DATA_FILE = path.join(ROOT, 'scripts/book_cover_data.json');
const OUT_DIR = path.join(ROOT, 'astro/public/assets/covers/books');
const RAW_DIR = path.join(OUT_DIR, '_raw');

const WIDTH = 1024;
const HEIGHT = 1448;
const GEN_WIDTH = 768;
const GEN_HEIGHT = 1086;
const CONCURRENCY = 1;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function parseArgs() {
  const args = new Set(process.argv.slice(2));
  const onlyArg = process.argv.slice(2).find((arg) => arg.startsWith('--only='));
  return {
    force: args.has('--force'),
    skipGenerate: args.has('--skip-generate'),
    only: onlyArg ? onlyArg.replace('--only=', '').split(',').map((s) => s.trim()).filter(Boolean) : null,
  };
}

function escapeXml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

function buildPrompt(book) {
  return [
    'Use case: historical-scene.',
    'Asset type: A4 portrait Bible book cover background.',
    `Primary request: photorealistic cover background for the Bible book ${book.name}.`,
    `Scene/backdrop: ${book.scene}.`,
    'Style/medium: realistic documentary photography, historically grounded ancient Near Eastern or first-century Mediterranean setting where appropriate.',
    'Composition/framing: vertical A4 portrait ratio, full bleed, cinematic but natural, strong central image, keep lower third visually calm for later title typography overlay.',
    'Lighting/mood: natural light, tactile materials, serious editorial tone.',
    'Constraints: no visible written text, no labels, no title, no watermark, no frame, no modern objects, no fantasy exaggeration.',
  ].join(' ');
}

async function fetchImageBuffer(prompt, seed, retries = 12) {
  const url =
    `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}` +
    `?width=${GEN_WIDTH}&height=${GEN_HEIGHT}&seed=${seed}&nologo=true`;

  for (let attempt = 1; attempt <= retries; attempt += 1) {
    try {
      const res = await fetch(url, {
        headers: { Accept: 'image/*' },
        signal: AbortSignal.timeout(35000),
      });

      if (res.ok) {
        const buffer = Buffer.from(await res.arrayBuffer());
        if (buffer.byteLength > 20000) return buffer;
      }

      if (res.status === 429) {
        await sleep(18000 * attempt);
        continue;
      }

      if (res.status !== 429 && res.status < 500) {
        throw new Error(`bad status ${res.status}`);
      }
    } catch (err) {
      if (attempt === retries) throw err;
    }

    await sleep(3500 * attempt);
  }

  throw new Error('exhausted retries');
}

function overlaySvg(book) {
  const titleSize = book.name.length >= 7 ? 82 : book.name.length >= 6 ? 90 : 102;
  const title = escapeXml(book.name);

  return Buffer.from(`
<svg xmlns="http://www.w3.org/2000/svg" width="${WIDTH}" height="${HEIGHT}" viewBox="0 0 ${WIDTH} ${HEIGHT}">
  <defs>
    <linearGradient id="bottomShade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000000" stop-opacity="0"/>
      <stop offset="0.35" stop-color="#000000" stop-opacity="0.3"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0.82"/>
    </linearGradient>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.45"/>
    </filter>
  </defs>
  <rect x="0" y="760" width="${WIDTH}" height="688" fill="url(#bottomShade)"/>
  <text x="${WIDTH / 2}" y="1158" text-anchor="middle"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="34" font-weight="600" letter-spacing="7"
    fill="#f8fafc" opacity="0.92" filter="url(#softShadow)">21세기 성경</text>
  <text x="${WIDTH / 2}" y="1278" text-anchor="middle"
    font-family="Apple SD Gothic Neo, Noto Serif CJK KR, Nanum Myeongjo, serif"
    font-size="${titleSize}" font-weight="700"
    fill="#ffffff" filter="url(#softShadow)">${title}</text>
  <line x1="392" y1="1332" x2="632" y2="1332" stroke="#ffffff" stroke-opacity="0.72" stroke-width="2"/>
  <text x="${WIDTH / 2}" y="1390" text-anchor="middle"
    font-family="Apple SD Gothic Neo, Noto Sans CJK KR, Nanum Gothic, sans-serif"
    font-size="30" font-weight="500" letter-spacing="3"
    fill="#f8fafc" opacity="0.82" filter="url(#softShadow)">현대 번역본</text>
</svg>`);
}

async function composeCover(book) {
  const raw = path.join(RAW_DIR, `${book.slug}.png`);
  const out = path.join(OUT_DIR, `${book.slug}.jpg`);

  await sharp(raw)
    .resize(WIDTH, HEIGHT, { fit: 'cover', position: 'attention' })
    .composite([{ input: overlaySvg(book), left: 0, top: 0 }])
    .jpeg({ quality: 88, mozjpeg: true })
    .toFile(out);
}

async function generateOne(book, index, options) {
  const raw = path.join(RAW_DIR, `${book.slug}.png`);
  const out = path.join(OUT_DIR, `${book.slug}.jpg`);

  if (!options.force) {
    try {
      await fs.access(out);
      console.log(`skip ${book.slug} ${book.name}`);
      return;
    } catch {
      // continue
    }
  }

  if (!options.skipGenerate) {
    const prompt = buildPrompt(book);
    const seed = 91000 + (index + 1) * 17;
    const buffer = await fetchImageBuffer(prompt, seed);
    await fs.writeFile(raw, buffer);
  }

  await composeCover(book);
  console.log(`done ${book.slug} ${book.name}`);
}

async function runPool(items, options) {
  let cursor = 0;
  const failed = [];

  const worker = async () => {
    while (cursor < items.length) {
      const index = cursor;
      cursor += 1;
      const book = items[index];

      try {
        await generateOne(book, index, options);
      } catch (err) {
        failed.push(book.slug);
        console.log(`fail ${book.slug} ${err?.message ?? err}`);
      }

      await sleep(900);
    }
  };

  await Promise.all(Array.from({ length: CONCURRENCY }, worker));

  if (failed.length) {
    throw new Error(`failed covers: ${failed.join(', ')}`);
  }
}

const options = parseArgs();
const allBooks = JSON.parse(await fs.readFile(DATA_FILE, 'utf8'));
const books = options.only ? allBooks.filter((book) => options.only.includes(book.slug)) : allBooks;

if (allBooks.length !== 66) {
  throw new Error(`expected 66 books, got ${allBooks.length}`);
}

await fs.mkdir(RAW_DIR, { recursive: true });
await runPool(books, options);
console.log('BOOK_COVERS_DONE');

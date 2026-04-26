import fs from 'node:fs/promises';
import path from 'node:path';

const ROOT = '/Users/will/workspace/bible/astro';
const CONTENT_DIR = path.join(ROOT, 'src/content/genesis');
const OUT_DIR = path.join(ROOT, 'public/assets/maps/genesis');

const START_CHAPTER = 4;
const END_CHAPTER = 50;
const CONCURRENCY = 2;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function chapterFile(chapter) {
  return path.join(CONTENT_DIR, `${String(chapter).padStart(2, '0')}.md`);
}

function outputFile(chapter) {
  return path.join(OUT_DIR, `ch${String(chapter).padStart(2, '0')}_chapter_scene.png`);
}

function parseTitle(markdown) {
  const match = markdown.match(/^title:\s*["']?(.+?)["']?\s*$/m);
  return match ? match[1].trim() : '장면';
}

function buildPrompt(chapter, title) {
  return [
    `Genesis chapter ${chapter}: ${title}.`,
    'photorealistic biblical historical reenactment scene,',
    'ancient near eastern geography and environment,',
    'historically grounded clothing and architecture,',
    'cinematic but natural light, realistic faces and textures,',
    'high detail, no fantasy exaggeration, no modern objects,',
    'no text, no title, no labels, no watermark, no frame'
  ].join(' ');
}

async function fetchImageBuffer(prompt, seed) {
  const url =
    `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}` +
    `?width=1536&height=1024&seed=${seed}&nologo=true&enhance=true`;

  for (let attempt = 1; attempt <= 8; attempt += 1) {
    try {
      const res = await fetch(url, {
        headers: { Accept: 'image/*' },
        signal: AbortSignal.timeout(45000),
      });

      if (res.ok) {
        const buf = Buffer.from(await res.arrayBuffer());
        if (buf.byteLength > 12000) return buf;
      }

      if (res.status !== 429 && res.status < 500) {
        throw new Error(`bad status ${res.status}`);
      }
    } catch (err) {
      if (attempt === 8) throw err;
    }

    await sleep(1800 * attempt);
  }

  throw new Error('exhausted retries');
}

async function generateOne(chapter) {
  const source = await fs.readFile(chapterFile(chapter), 'utf8');
  const title = parseTitle(source);
  const prompt = buildPrompt(chapter, title);
  const seed = 48000 + chapter;
  const file = outputFile(chapter);

  const buffer = await fetchImageBuffer(prompt, seed);
  await fs.writeFile(file, buffer);
  console.log(`done ch${String(chapter).padStart(2, '0')} ${title}`);
}

async function runPool(items, concurrency) {
  let cursor = 0;

  const worker = async () => {
    while (true) {
      const idx = cursor;
      cursor += 1;
      if (idx >= items.length) return;
      await generateOne(items[idx]);
      await sleep(500);
    }
  };

  await Promise.all(Array.from({ length: concurrency }, worker));
}

await fs.mkdir(OUT_DIR, { recursive: true });

const chapters = Array.from(
  { length: END_CHAPTER - START_CHAPTER + 1 },
  (_, i) => START_CHAPTER + i
);

console.log(`generating chapters ${START_CHAPTER}-${END_CHAPTER}...`);
await runPool(chapters, CONCURRENCY);
console.log('GENESIS_CH04_50_DONE');

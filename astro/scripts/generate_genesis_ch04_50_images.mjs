import fs from 'node:fs/promises';
import path from 'node:path';

const ROOT = '/Users/will/workspace/bible/astro';
const CONTENT_DIR = path.join(ROOT, 'src/content/genesis');
const OUT_DIR = path.join(ROOT, 'public/assets/maps/genesis');

const START_CHAPTER = 4;
const END_CHAPTER = 50;
const CONCURRENCY = 1;

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

async function fetchImageBuffer(prompt, seed, retries = 10) {
  const url =
    `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}` +
    `?width=1536&height=1024&seed=${seed}&nologo=true&enhance=true`;

  for (let attempt = 1; attempt <= retries; attempt += 1) {
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
      if (attempt === retries) throw err;
    }

    await sleep(2200 * attempt);
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

async function runPool(items, concurrency, failed) {
  let cursor = 0;

  const worker = async () => {
    while (true) {
      const idx = cursor;
      cursor += 1;
      if (idx >= items.length) return;
      const ch = items[idx];
      try {
        await generateOne(ch);
      } catch (err) {
        failed.push(ch);
        console.log(`fail ch${String(ch).padStart(2, '0')} ${err?.message ?? err}`);
      }
      await sleep(700);
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
const failed = [];
await runPool(chapters, CONCURRENCY, failed);

if (failed.length) {
  console.log(`retrying failed chapters: ${failed.join(', ')}`);
  for (const ch of failed.slice()) {
    try {
      await generateOne(ch);
      const idx = failed.indexOf(ch);
      if (idx >= 0) failed.splice(idx, 1);
    } catch (err) {
      console.log(`retry-fail ch${String(ch).padStart(2, '0')} ${err?.message ?? err}`);
    }
    await sleep(1400);
  }
}

if (failed.length) {
  throw new Error(`still failed chapters: ${failed.join(', ')}`);
}

console.log('GENESIS_CH04_50_DONE');

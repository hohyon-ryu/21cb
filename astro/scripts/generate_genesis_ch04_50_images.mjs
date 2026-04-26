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

const SCENE_BRIEFS = {
  4: 'Cain and Abel offer sacrifices, then Cain kills Abel in a field east of Eden.',
  5: 'A long genealogy from Adam to Noah is remembered across generations.',
  6: 'Violence fills the earth as Noah prepares the ark before the flood.',
  7: 'Heavy rain and rising waters begin the flood as the ark is sealed.',
  8: 'Waters recede, the ark rests in highlands, and Noah waits for dry land.',
  9: 'After the flood, the rainbow covenant is set over a renewed earth.',
  10: 'Peoples and nations spread in many directions after Noah.',
  11: 'The tower project at Shinar collapses and people disperse by language.',
  12: 'Abram leaves his homeland and travels toward Canaan and Egypt.',
  13: 'Abram and Lot separate, one toward Jordan plain and one toward hill country.',
  14: 'A regional war of kings unfolds, and Abram rescues Lot.',
  15: 'A covenant is established under a star-filled night sky.',
  16: 'Hagar flees into desert wilderness and meets God by a spring.',
  17: 'Covenant identity is marked in Abraham\'s camp.',
  18: 'Visitors come to Abraham near Mamre with a promise of Isaac.',
  19: 'Sodom is judged; Lot\'s family flees toward Zoar.',
  20: 'Abraham and Sarah stay in Gerar under political tension.',
  21: 'Isaac is born; Hagar and Ishmael move through Beersheba wilderness.',
  22: 'Abraham and Isaac ascend a mountain in Moriah for a severe test.',
  23: 'Sarah is buried at Machpelah near Hebron, securing family land.',
  24: 'A long journey finds Rebekah from Aram-Naharaim for Isaac.',
  25: 'Patriarchal generations shift from Abraham to Isaac to Jacob and Esau.',
  26: 'Isaac lives in Gerar and disputes over desert wells.',
  27: 'Jacob receives the blessing through deception and then flees.',
  28: 'Jacob dreams at Bethel on the road north toward Haran.',
  29: 'Jacob arrives in Haran and begins family life with Leah and Rachel.',
  30: 'Household growth and livestock conflict shape Jacob\'s years in Aram.',
  31: 'Jacob departs secretly from Laban and heads back toward Gilead.',
  32: 'Jacob fears Esau, crosses Jabbok, and wrestles through the night.',
  33: 'Jacob and Esau meet again and reconcile after years apart.',
  34: 'Dinah incident triggers violent retaliation at Shechem.',
  35: 'The family returns to Bethel; Rachel dies near Bethlehem.',
  36: 'Esau\'s line settles in Seir and Edom\'s chiefs emerge.',
  37: 'Joseph is sold by his brothers and taken south toward Egypt.',
  38: 'Judah and Tamar story unfolds in Canaanite towns.',
  39: 'Joseph serves in Potiphar\'s house and is sent to prison.',
  40: 'In prison, Joseph interprets the dreams of two royal officials.',
  41: 'Pharaoh\'s dreams elevate Joseph to power in Egypt.',
  42: 'Famine drives the first trip of Jacob\'s sons from Canaan to Egypt.',
  43: 'A second journey to Egypt includes Benjamin and hard negotiation.',
  44: 'Joseph tests his brothers with the silver cup trap.',
  45: 'Joseph reveals himself and reframes history through providence.',
  46: 'Jacob\'s household migrates from Canaan to Goshen in Egypt.',
  47: 'Settlement in Goshen and famine-era grain policy reshape society.',
  48: 'Jacob blesses Ephraim and Manasseh in Egypt.',
  49: 'Jacob blesses the twelve sons, defining tribal futures.',
  50: 'A grand funeral procession carries Jacob to Machpelah, then returns to Egypt.',
};

function geoHint(chapter) {
  if (chapter <= 11) {
    return 'Mesopotamia core: lower Tigris-Euphrates, Shinar/Babylonia, Ararat highlands, Persian Gulf context';
  }
  if (chapter <= 25) {
    return 'Abram era corridor: Ur to Haran to Canaan, Negev, Hebron, Beersheba, Jordan valley, and Egypt delta';
  }
  if (chapter <= 36) {
    return 'Jacob era corridor: Canaan highlands, Bethel, Shechem, Jabbok, Gilead, Haran, and Seir/Edom';
  }
  return 'Joseph era corridor: Canaan to Nile delta Egypt, Goshen, and route toward Hebron/Machpelah';
}

const COMPOSITION_MODES = [
  'wide aerial documentary perspective',
  'ground-level cinematic perspective',
  'river-valley panorama with human scale',
  'dusty caravan-road perspective',
  'dawn low-angle historical realism',
  'late-evening camp realism',
  'palace-court realism with geographic backdrop',
  'mountain-pass perspective with depth',
  'desert-edge perspective near cultivated land',
  'bird-eye regional geography emphasis',
];

function buildPrompt(chapter, title) {
  const brief = SCENE_BRIEFS[chapter] ?? `Genesis chapter ${chapter} scene.`;
  const mode = COMPOSITION_MODES[(chapter - START_CHAPTER) % COMPOSITION_MODES.length];
  const area = geoHint(chapter);

  return [
    `Genesis chapter ${chapter}. Title: ${title}. ${brief}`,
    'Create one photorealistic historical image with strong geographic readability.',
    'Blend a realistic biblical reenactment scene and a modern terrain map in one continuous composition, smooth feather blend, no hard split panels.',
    `Geographic focus: ${area}.`,
    'Use real present-day landforms, coastlines, and river paths of the Middle East; include faint modern country borders where relevant.',
    'Highlight chapter-relevant route or location with subtle color emphasis integrated into the terrain.',
    'If map labels appear, write them directly on map terrain in Korean and English, never in white overlay boxes.',
    `Visual composition style: ${mode}.`,
    'Natural color grading, high-detail documentary realism, believable people, clothing, tools, architecture, and climate.',
    'No fantasy elements, no modern machines, no UI text, no title bar, no watermark, no frame, no collage border.',
  ].join(' ');
}

async function fetchImageBuffer(prompt, seed, retries = 8) {
  const url =
    `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}` +
    `?width=1536&height=1024&seed=${seed}&nologo=true&enhance=true`;

  for (let attempt = 1; attempt <= retries; attempt += 1) {
    try {
      const res = await fetch(url, {
        headers: { Accept: 'image/*' },
        signal: AbortSignal.timeout(60000),
      });

      if (res.ok) {
        const buf = Buffer.from(await res.arrayBuffer());
        if (buf.byteLength > 16000) return buf;
      }

      if (res.status !== 429 && res.status < 500) {
        throw new Error(`bad status ${res.status}`);
      }
    } catch (err) {
      if (attempt === retries) throw err;
    }

    await sleep(2500 * attempt);
  }

  throw new Error('exhausted retries');
}

async function generateOne(chapter) {
  const source = await fs.readFile(chapterFile(chapter), 'utf8');
  const title = parseTitle(source);
  const prompt = buildPrompt(chapter, title);
  const seed = 73000 + chapter * 13;
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
      await sleep(900);
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
    await sleep(1600);
  }
}

if (failed.length) {
  throw new Error(`still failed chapters: ${failed.join(', ')}`);
}

console.log('GENESIS_CH04_50_DONE');

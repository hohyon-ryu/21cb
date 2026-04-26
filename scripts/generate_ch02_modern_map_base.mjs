import fs from "node:fs/promises";
import path from "node:path";

const outDir = "/Users/will/workspace/bible/site/assets/maps/genesis/candidates_modern";
const seeds = [9311, 9312, 9313, 9314];

const prompt =
  "modern satellite topographic map of mesopotamia and levant, real current terrain and coastline, clear tigris and euphrates river system flowing into persian gulf, southern iraq highlighted by terrain only, natural earth colors, no antique paper, no fantasy style, no text, no title, no legend, no labels, no UI";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function fetchImage(seed) {
  const url = `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?width=1536&height=1024&seed=${seed}&nologo=true&enhance=true`;

  for (let i = 1; i <= 8; i += 1) {
    try {
      const res = await fetch(url, {
        headers: { Accept: "image/*" },
        signal: AbortSignal.timeout(30000)
      });
      if (res.ok) {
        const buf = Buffer.from(await res.arrayBuffer());
        if (buf.byteLength > 10000) return buf;
      }
      if (res.status !== 429 && res.status < 500) {
        throw new Error(`status ${res.status}`);
      }
    } catch (err) {
      if (i === 8) throw err;
    }
    await sleep(2500 * i);
  }
  throw new Error("retry exhausted");
}

await fs.mkdir(outDir, { recursive: true });

for (const seed of seeds) {
  const file = `ch02_modern_base_${seed}.png`;
  const target = path.join(outDir, file);
  try {
    await fs.access(target);
    console.log(`skip ${file}`);
    continue;
  } catch {}

  console.log(`generate ${file}`);
  const buf = await fetchImage(seed);
  await fs.writeFile(target, buf);
}

console.log("CH02_MODERN_BASE_DONE");

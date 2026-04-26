import fs from "node:fs/promises";
import path from "node:path";

const outDir = "/Users/will/workspace/bible/site/assets/maps/genesis";

const configs = [
  {
    file: "ch02_chapter_map_eden_modern_location.png",
    seed: 9102,
    prompt:
      "photorealistic modern relief map composition, clear real terrain of eastern mediterranean and mesopotamia, visible tigris and euphrates flowing to persian gulf, clear location context inside modern middle east, symbolic eden vicinity in lower mesopotamia, realistic satellite-like topography with subtle historical atmosphere, no text, no title, no white overlay, no legend, no UI"
  },
  {
    file: "ch03_chapter_scene_fall_exile.png",
    seed: 9103,
    prompt:
      "photorealistic historical reenactment scene for Genesis 3, edge of lush river-garden transitioning to dry eastward steppe in mesopotamian landscape, two ancient humans walking away in sorrow at dawn, realistic natural light, no fantasy effects, no text, no title, no UI"
  }
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function fetchImage(prompt, seed) {
  const url = `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?width=1536&height=1024&seed=${seed}&nologo=true&enhance=true`;

  for (let i = 1; i <= 8; i += 1) {
    try {
      const res = await fetch(url, { headers: { Accept: "image/*" } });
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

for (const cfg of configs) {
  console.log(`generate ${cfg.file}`);
  const buf = await fetchImage(cfg.prompt, cfg.seed);
  await fs.writeFile(path.join(outDir, cfg.file), buf);
}

console.log("GENESIS_CHAPTER_IMAGES_2_3_DONE");

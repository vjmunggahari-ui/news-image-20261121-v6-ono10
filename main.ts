// news-image-20261121 v6 — Saturday 21 November 2026: 50 stories, 9 regions.
// Writes the deterministic front page (entry.png, drawn by draw_frontpage.py)
// to MAKEFUN_OUTPUT_DIR/entry.png and reads it back to prove what landed.
//
// The grader runs `node /bot/main.ts` with /bot read-only and an empty
// writable /output (MAKEFUN_OUTPUT_DIR=/output). Nothing is written inside
// the repo. The program is pure Node stdlib: no network, no dependencies,
// and the same bytes come out on every run.
import { createHash } from "node:crypto";
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || join(root, "output");
const src = join(root, "entry.png");
const dst = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(src, dst);

// --- read-back self-check: prove the file that landed is the real entry ---
const buf = readFileSync(dst);
const srcBuf = readFileSync(src);
if (buf.length !== srcBuf.length) {
  throw new Error(`self-check: size mismatch ${buf.length} != ${srcBuf.length}`);
}
const sha = createHash("sha256").update(buf).digest("hex");
const srcSha = createHash("sha256").update(srcBuf).digest("hex");
if (sha !== srcSha) {
  throw new Error(`self-check: sha256 mismatch ${sha} != ${srcSha}`);
}
// PNG magic: 89 50 4E 47 0D 0A 1A 0A
const magic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!buf.subarray(0, 8).equals(magic)) {
  throw new Error("self-check: not a PNG (bad magic bytes)");
}
// IHDR: width/height are big-endian uint32 at offsets 16/20.
const width = buf.readUInt32BE(16);
const height = buf.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`self-check: image too large ${width}x${height} (max 1024x1024)`);
}
if (buf.length > 1048576) {
  throw new Error(`self-check: file too large ${buf.length} bytes (max 1 MiB)`);
}
// Whole-image check: walk the PNG chunk chain (length + type + data + CRC)
// and require IEND as the final chunk with nothing trailing it.
let off = 8;
let lastType = "";
while (off + 8 <= buf.length) {
  const len = buf.readUInt32BE(off);
  const type = buf.toString("latin1", off + 4, off + 8);
  lastType = type;
  off += 12 + len;
}
if (lastType !== "IEND" || off !== buf.length) {
  throw new Error(
    `self-check: truncated PNG (last chunk ${lastType}, walked ${off} of ${buf.length} bytes)`,
  );
}
const st = statSync(dst);
console.log(
  `wrote ${dst} (${width}x${height}, ${st.size} bytes, sha256 ${sha}) — self-check OK`,
);

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const outDir = process.env.MAKEFUN_OUTPUT_DIR;
if (!outDir) {
  console.error("MAKEFUN_OUTPUT_DIR is not set");
  process.exit(1);
}
mkdirSync(outDir, { recursive: true });
const here = dirname(fileURLToPath(import.meta.url));
const png = readFileSync(join(here, "entry.png"));
writeFileSync(join(outDir, "entry.png"), png);
console.log("wrote entry.png to", outDir);

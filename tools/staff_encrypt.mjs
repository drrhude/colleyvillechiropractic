// Encrypts the staff product database for /staff/ (the repo is public, so the
// plaintext file must never be committed).
//
//   node tools/staff_encrypt.mjs path/to/products.json "your password"
//
// Writes staff/data.enc.json. Same format the page itself exports from
// Settings > "Download updated data file", so either route works.
import { readFileSync, writeFileSync } from "node:fs";
import { webcrypto as crypto } from "node:crypto";

const [, , src, password] = process.argv;
if (!src || !password) {
  console.error('Usage: node tools/staff_encrypt.mjs products.json "password"');
  process.exit(1);
}
const ITER = 310000;
const enc = new TextEncoder();
const b64 = (u8) => Buffer.from(u8).toString("base64");

const data = JSON.parse(readFileSync(src, "utf8"));
const salt = crypto.getRandomValues(new Uint8Array(16));
const iv = crypto.getRandomValues(new Uint8Array(12));
const base = await crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2", false, ["deriveKey"]);
const key = await crypto.subtle.deriveKey(
  { name: "PBKDF2", hash: "SHA-256", salt, iterations: ITER },
  base, { name: "AES-GCM", length: 256 }, false, ["encrypt"]);
const ct = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, enc.encode(JSON.stringify(data))));

const out = { v: 1, kdf: "PBKDF2-SHA256", iter: ITER, salt: b64(salt), iv: b64(iv), ct: b64(ct) };
const dest = new URL("../staff/data.enc.json", import.meta.url);
writeFileSync(dest, JSON.stringify(out));
console.log(`Encrypted ${data.products?.length ?? "?"} products -> staff/data.enc.json`);

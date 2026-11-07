// MIT. Bounded, deterministic differential audit; no upstream tables or fixtures.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { execFile } from "node:child_process";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

if (process.argv.length !== 4) {
  console.error("Usage: node tools/audit-context.mjs /path/to/avro-lib.js /path/to/report.json");
  process.exit(2);
}
const sha256 = (data) => createHash("sha256").update(data).digest("hex");
const source = readFileSync(process.argv[2]);
const referenceSha256 = "312ed3438ebf0a69f6de38036572ec39cdbafe3ef53f500caa402aaa704c2b32";
assert.equal(sha256(source), referenceSha256, "Use the pinned v1.1.4 parser");
const context = vm.createContext({});
vm.runInContext(source.toString("utf8"), context, { timeout: 5000 });
const parse = (input) => context.OmicronLab.Avro.Phonetic.parse(input);
const points = (value) => [...value].map((ch) =>
  `U+${ch.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}`).join(" ");

// A token here is an authored input fragment, not a claim about scanner matches.
// Concatenation deliberately exposes overlaps across fragment boundaries.
const groups = new Map();
const add = (group, raw) => {
  if (!groups.has(group)) groups.set(group, new Set());
  groups.get(group).add(raw);
};
const mixed = ["a", "i", "I", "u", "U", "e", "ee", "o", "O", "oo", "OI", "OU",
  "rri", "aZ", "oZ", "y", "Y", "Z", "w", "x", "ng", "Ng", "NG", "r", "rr", "k"];
for (const prefix of ["", "k", "ng", "rrq"]) {
  for (const a of mixed) for (const b of mixed) for (const c of mixed) {
    add("mixed-triples", prefix + a + b + c);
  }
}
const nasalReph = ["ng", "Ng", "NG", "ngr", "Ngr", "NGr", "n", "N", "rr", "rrr",
  "rrq", "rrw", "rrx", "rrY", "rry", "rrZ", "rrNg", "rrng", "rrShN", "rrkShm"];
for (const a of nasalReph) for (const b of nasalReph) {
  for (const end of ["", "a", "i", "ee", "o", "rri", "y", "Z", "r", "rr", "ry", "rri`", "`rrq"]) {
    add("nasal-reph", a + b + end);
  }
}
const consumed = ["k", "kh", "kk", "kkh", "kSh", "kx", "kkhN", "kShm", "Ngk", "Ngkh",
  "Ngkx", "Ngkkh", "NgkSh", "Nggh", "ng", "ngh", "NG", "nch", "njh", "cch", "jjh",
  "bdh", "bDh", "Gdh", "GG", "gG", "Gg", "Jh", "sh", "Sh", "ShN", "rrq", "kr", "krr",
  "Ngr", "NGrr", "aZr", "wrr", "xrr", "t``", "nt``"];
for (const left of consumed) {
  for (const right of ["h", "N", "g", "G", "r", "rr", "rrr", "rri", "rrq", "rrRh", "y", "Z", "w", "x", "ng", "aZ", "oZ"]) {
    for (const end of ["", "a", "o", "ry", "rri", "`rrq"]) {
      add("consumed-exposed", left + right + end);
    }
  }
}
const aliases = ["A", "B", "C", "E", "F", "H", "K", "L", "M", "P", "Q", "V", "W", "X",
  "SH", "kH", "KSH", "NgK", "nG", "GG", "Gg", "gG", "JH", "Jh"];
for (const a of aliases) for (const b of aliases) {
  for (const end of ["", "a", "y", "rri", "rrq", "`a"]) add("ascii-aliases", a + b + end);
}
const boundaries = [" ", "!", ".", "..", "...", ".`", ":", ":`", "^", "^`", ",,", "$", "`", "``",
  "a`", "o`", "rri`", "t``", "1", "৯", "ক", "র", "é", "🙂", "\u0301", "\u200C", "\u200D",
  "\0", "\n", "\r", "\t"];
for (const left of ["", "k", "ng", "r", "rr", "rrq", "aZ", "w", "x", "t", "nt"]) {
  for (const boundary of boundaries) {
    for (const right of ["", "a", "y", "Z", "w", "x", "rrq", "rri", "ng", "`a"]) {
      add("symbols-unicode-boundaries", left + boundary + right);
    }
  }
}
// Inventory-driven probes exercise every pinned spelling independently. Contexts
// are authored here, not copied from reference rule conditions or replacements.
const spellings = context.OmicronLab.Avro.Phonetic.data.patterns.map((item) => item.find);
for (const spelling of spellings) {
  for (const prefix of ["", "a", "k", "ng", "rr", "1", "🙂", "`", "r`", "aZ"]) {
    for (const suffix of ["", "a", "i", "o", "r", "rr", "ry", "rri", "`", "``", "y", "Z", "ng", ".", "🙂"]) {
      add("all-spellings-contexts", prefix + spelling + suffix);
    }
  }
  // Exercise insensitive aliases and sensitive forms, including mixed digraphs.
  const variants = [...spelling].reduce((forms, ch) =>
    [...new Set(forms.flatMap((form) => [form + ch.toLowerCase(), form + ch.toUpperCase()]))], [""]);
  for (const variant of variants) {
    for (const end of ["", "a", "r", "rri", "`a"]) add("all-spellings-case", variant + end);
  }
}
// Keep known Unicode case policy differences separate; do not excuse any other gap.
const policy = ["İ", "É", "Σ"];
for (const raw of policy) add("unicode-case-policy", raw);
add("symbols-unicode-boundaries", "");
const inputs = [...new Set([...groups.values()].flatMap((group) => [...group]))];

const root = fileURLToPath(new URL("../", import.meta.url));
const run = (command, args, input) => new Promise((resolve, reject) => {
  const child = execFile(command, args, { cwd: root, encoding: "buffer", maxBuffer: 128 * 1024 * 1024 },
    (error, stdout, stderr) => {
      if (error) reject(new Error(`${command} failed: ${stderr.toString()}`, { cause: error }));
      else resolve(stdout);
    });
  child.stdin.on("error", (error) => reject(error));
  child.stdin.end(input);
});
const build = await run("cargo", ["build", "--offline", "--locked", "--release", "--example", "audit_batch", "--message-format=json"]);
const artifacts = build.toString().trim().split("\n").map((line) => JSON.parse(line));
const executable = artifacts.find((item) => item.reason === "compiler-artifact" && item.target.name === "audit_batch")?.executable;
assert.ok(executable, "Cargo must report the batch executable");
const frames = inputs.map((input) => {
  const bytes = Buffer.from(input);
  const header = Buffer.alloc(4);
  header.writeUInt32LE(bytes.length);
  return Buffer.concat([header, bytes]);
});
const output = await run(executable, [], Buffer.concat(frames));
const actual = new Map();
const decoder = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true });
let offset = 0;
for (const input of inputs) {
  assert.ok(offset + 4 <= output.length, "Missing response length");
  const size = output.readUInt32LE(offset);
  offset += 4;
  assert.ok(offset + size <= output.length, "Truncated response");
  actual.set(input, decoder.decode(output.subarray(offset, offset + size)));
  offset += size;
}
assert.equal(offset, output.length, "Unexpected extra response bytes");

const expected = new Map(inputs.map((raw) => [raw, parse(raw)]));
const differences = [];
const groupReports = [];
for (const [name, cases] of groups) {
  const records = [...cases].map((raw) => [raw, actual.get(raw), expected.get(raw)]);
  const gaps = records.filter(([, result, reference]) => result !== reference);
  groupReports.push({ name, inputs: cases.size, differences: gaps.length, sha256: sha256(JSON.stringify(records)) });
  for (const [input, engine, reference] of gaps) {
    differences.push({ group: name, input, engine, reference, enginePoints: points(engine), referencePoints: points(reference) });
  }
  console.log(`${name}: ${cases.size} inputs, ${gaps.length} differences`);
}
const unexpected = differences.filter((item) => item.group !== "unicode-case-policy");
const policyDifferences = differences.filter((item) => item.group === "unicode-case-policy");
const report = {
  schema: 1, scope: "mixed-context-v2", referenceSha256,
  auditSha256: sha256(readFileSync(fileURLToPath(import.meta.url))),
  transportSha256: sha256(readFileSync(new URL("../examples/audit_batch.rs", import.meta.url))),
  node: process.version,
  rustc: (await run("rustc", ["--version"])).toString().trim(),
  cargo: (await run("cargo", ["--version"])).toString().trim(),
  uniqueInputs: inputs.length,
  groups: groupReports,
  unexpectedDifferences: unexpected.length,
  policyDifferences: policyDifferences.length,
  differences,
};
writeFileSync(process.argv[3], JSON.stringify(report, null, 2) + "\n");
// Assert the known policy outputs too; a changed or resolved probe needs review.
assert.deepEqual(policy.map((raw) => actual.get(raw)), ["İ", "É", "Σ"]);
assert.deepEqual(policy.map((raw) => expected.get(raw)), ["ই\u0307", "é", "σ"]);
console.log(`${inputs.length} unique inputs; ${unexpected.length} unexpected differences; ${policyDifferences.length} known policy differences`);
process.exitCode = unexpected.length ? 1 : 0;

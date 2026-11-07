// MIT. Runs our authored fixtures against an external, pinned reference file.
// The reference is not bundled with or used by the Rust library.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import vm from "node:vm";

if (![3, 4].includes(process.argv.length)) {
  console.error("Usage: node tools/check-reference.mjs /path/to/avro-lib.js [coverage-report.json]");
  process.exit(2);
}

const source = readFileSync(process.argv[2]);
assert.equal(
  createHash("sha256").update(source).digest("hex"),
  "312ed3438ebf0a69f6de38036572ec39cdbafe3ef53f500caa402aaa704c2b32",
  "Reference must be src/avro-lib.js from the pinned v1.1.4 revision",
);
const context = vm.createContext({});
vm.runInContext(source.toString("utf8"), context, { timeout: 5000 });
const parse = (input) => context.OmicronLab.Avro.Phonetic.parse(input);
const codePoints = (text) =>
  [...text]
    .map((ch) => `U+${ch.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}`)
    .join(" ");

// Trace only the external reference in an isolated VM. Output assertions below
// still use the untouched parser; this instrumentation measures selected matches,
// not mere substring presence or exhaustive reachability of contextual rules.
const traceContext = vm.createContext({ hits: [] });
const instrumented = source.toString("utf8")
  .replace("output += rule.replace;", "hits.push([i, j]); output += rule.replace;")
  .replace("output += pattern.replace;", "hits.push([i, -1]); output += pattern.replace;");
for (const statement of ["output += rule.replace;", "output += pattern.replace;"]) {
  assert.equal(source.toString("utf8").split(statement).length, 2,
    `Expected one instrumentation site: ${statement}`);
}
vm.runInContext(instrumented, traceContext, { timeout: 5000 });
const patterns = context.OmicronLab.Avro.Phonetic.data.patterns;
const selected = patterns.map(() => new Set());
const standalone = new Set();
const inputs = new Map();
const fixtureCounts = {};
const fixtureHash = createHash("sha256");
const testSource = readFileSync(new URL("../tests/conversion.rs", import.meta.url), "utf8");
const rustFixtures = new Set([...testSource.matchAll(/include_str!\(\s*"fixtures\/([^"\n]+)"\s*,?\s*\)/g)]
  .map((match) => match[1]));
const names = readdirSync(new URL("../tests/fixtures/", import.meta.url))
  .filter((name) => name.endsWith(".tsv") && name !== "unicode-case-policy.tsv").sort();
let count = 0;
for (const name of names) {
  assert.ok(rustFixtures.has(name),
    `${name} must remain in the Rust regression suite`);
  const fixture = readFileSync(
    new URL(`../tests/fixtures/${name}`, import.meta.url),
    "utf8",
  );
  fixtureHash.update(JSON.stringify([name, fixture]));
  let fileCount = 0;
  for (const line of fixture.trimEnd().split("\n")) {
    if (line.startsWith("#")) continue;
    const columns = line.split("\t");
    assert.equal(columns.length, 3, `Invalid fixture: ${line}`);
    const [input, expected, points] = columns;
    const actual = parse(input);
    assert.equal(actual, expected, `Reference output for ${JSON.stringify(input)}`);
    assert.equal(codePoints(actual), points, `Code points for ${JSON.stringify(input)}`);
    if (inputs.has(input)) {
      assert.equal(inputs.get(input), expected, `Conflicting fixture: ${JSON.stringify(input)}`);
    }
    inputs.set(input, expected);
    standalone.add(input);
    traceContext.hits.length = 0;
    assert.equal(traceContext.OmicronLab.Avro.Phonetic.parse(input), actual,
      "Tracing must preserve reference output");
    for (const [pattern, rule] of traceContext.hits) selected[pattern].add(rule);
    fileCount += 1;
  }
  assert.ok(fileCount > 0, `${name} must contain cases`);
  count += fileCount;
  fixtureCounts[name] = fileCount;
}
console.log(`PASS: ${count} authored cases; runtime ${process.version}`);

// Deliberate policy exceptions have independent engine/reference expectations.
// Rust tests check the engine columns; these rows never inflate parity counts.
const policyFixture = readFileSync(
  new URL("../tests/fixtures/unicode-case-policy.tsv", import.meta.url), "utf8",
);
fixtureHash.update(JSON.stringify(["unicode-case-policy.tsv", policyFixture]));
const policyInputs = new Set();
let policyDifferences = 0;
for (const line of policyFixture.trimEnd().split("\n")) {
  if (line.startsWith("#")) continue;
  const columns = line.split("\t");
  assert.equal(columns.length, 5, `Invalid policy fixture: ${line}`);
  const [input, engine, enginePoints, reference, referencePoints] = columns;
  assert.ok(!policyInputs.has(input), `Duplicate policy input: ${JSON.stringify(input)}`);
  policyInputs.add(input);
  assert.equal(codePoints(engine), enginePoints, `Engine policy code points: ${JSON.stringify(input)}`);
  const actual = parse(input);
  assert.equal(actual, reference, `Reference policy output: ${JSON.stringify(input)}`);
  assert.equal(codePoints(actual), referencePoints, `Reference policy code points: ${JSON.stringify(input)}`);
  if (engine !== reference) policyDifferences += 1;
}
assert.ok(policyInputs.size > 0, "Unicode policy fixture must contain cases");
console.log(`PASS: ${policyInputs.size} Unicode policy cases (${policyDifferences} deliberate differences, ${policyInputs.size - policyDifferences} agreements); separate from parity fixtures`);

// A standalone spelling, a selected pattern, and a contextual branch are distinct
// coverage measures. None proves every ordering or interaction is compatible.
const inventory = patterns.map((pattern, index) => ({
  index, spelling: pattern.find,
  standaloneFixture: standalone.has(pattern.find),
  selected: selected[index].size > 0,
  defaultSelected: selected[index].has(-1),
  contextualRules: (pattern.rules ?? []).length,
  selectedRules: [...selected[index]].filter((rule) => rule >= 0).sort((a, b) => a - b),
}));
const family = (spelling) => {
  if (spelling.includes("`")) return "escapes";
  if (/^[0-9]$/.test(spelling)) return "digits";
  if (/^[^a-zA-Z0-9]+$/.test(spelling)) return "symbols";
  if (/^(a|aZ|AZ|i|I|u|U|e|ee|o|oo|oZ|O|OI|OU|rri)$/.test(spelling)) return "vowels";
  if (/^(ng|Ng|NG)/.test(spelling)) return "nasal-prefixed";
  if (/^[rR]/.test(spelling)) return "r-and-reph";
  return spelling.length === 1 ? "single-consonants" : "digraphs-and-conjuncts";
};
const families = {};
for (const item of inventory) {
  const name = family(item.spelling);
  families[name] ??= { patterns: 0, selected: 0, contextualRules: 0, selectedRules: 0 };
  families[name].patterns += 1;
  families[name].selected += Number(item.selected);
  families[name].contextualRules += item.contextualRules;
  families[name].selectedRules += item.selectedRules.length;
}
const missingSpellings = inventory.filter((item) => !item.standaloneFixture).map((item) => item.spelling);
const unselectedPatterns = inventory.filter((item) => !item.selected).map((item) => ({ index: item.index, spelling: item.spelling }));
const unselectedRules = inventory.flatMap((item) =>
  Array.from({ length: item.contextualRules }, (_, index) => index)
    .filter((index) => !item.selectedRules.includes(index))
    .map((rule) => ({ index: item.index, spelling: item.spelling, rule })));
const report = {
  schema: 1,
  referenceSha256: createHash("sha256").update(source).digest("hex"),
  checkerSha256: createHash("sha256").update(readFileSync(new URL(import.meta.url))).digest("hex"),
  node: process.version,
  fixturesSha256: fixtureHash.digest("hex"),
  fixtureFiles: names.length, fixtureRows: count, uniqueInputs: inputs.size,
  duplicateRows: count - inputs.size,
  policyCases: policyInputs.size, policyDifferences,
  families,
  patternCount: patterns.length,
  contextualRules: inventory.reduce((sum, item) => sum + item.contextualRules, 0),
  missingSpellings, unselectedPatterns, unselectedRules, fixtureCounts, inventory,
};
console.log(`Coverage: ${patterns.length} patterns; ${missingSpellings.length} missing standalone spellings; ${unselectedPatterns.length} unselected patterns; ${unselectedRules.length} unselected contextual rules`);
console.log(JSON.stringify({ missingSpellings, unselectedPatterns, unselectedRules }));
if (process.argv[3]) writeFileSync(process.argv[3], JSON.stringify(report, null, 2) + "\n");

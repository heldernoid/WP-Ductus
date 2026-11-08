// Run the browser engine (web/ductus.js) on cases from a JSON file and print the scalar outputs as JSON.
// Used by tests/test_parity.py: node tests/parity.mjs cases.json
import { readFileSync } from "node:fs";
import { Net, inputs } from "../web/ductus.js";

const root = new URL("../", import.meta.url);
const arch = JSON.parse(readFileSync(new URL("web/model/arch.json", root)));
const net = new Net(arch, readFileSync(new URL("web/model/ductus.edits", root), "utf8"));
const cases = JSON.parse(readFileSync(process.argv[2]));
const out = cases.map(c => {
  const T = net.forward(inputs(c.model, c.attempt, c.pressure, c.copy));
  return Object.fromEntries(Object.entries(T).filter(([, v]) => typeof v === "number"));
});
console.log(JSON.stringify(out));

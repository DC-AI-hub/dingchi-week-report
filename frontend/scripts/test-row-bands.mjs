import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import vm from "node:vm"
import ts from "typescript"

const source = readFileSync(new URL("../src/shared/table/row-bands.ts", import.meta.url), "utf8")
const code = ts.transpileModule(source, {compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText
const module = {exports:{}}
vm.runInNewContext(code, {module,exports:module.exports})
const band = rows => Array.from(module.exports.rowBands(rows))
const row = (...spans) => ({spans})
assert.deepEqual(band([row(1),row(1),row(1),row(1)]),["base","alternate","base","alternate"])
// 客户合并3行，其内任务再分组合并：整个客户组必须保持相同底色。
assert.deepEqual(band([row(3,2),row(1),row(1),row(2),row(1),row(1)]),["base","base","base","alternate","alternate","base"])
// 交叠的合并单元格必须形成一个连续组。
assert.deepEqual(band([row(2),row(3),row(1),row(1),row(1)]),["base","base","base","base","alternate"])
// 展开多个子变更后，后续主行的交替背景不变。
assert.deepEqual(band([row(1),{spans:[],kind:"change"},{spans:[],kind:"change"},row(1),row(1)]),["base","change","change","alternate","base"])
assert.deepEqual(band([row(0),row(1),row(1)]),["base","base","base"])
assert.deepEqual(band([{spans:[],kind:"empty"},row(1),row(1)]),["empty","base","alternate"])
assert.deepEqual(band([]),[])
console.log("PASS: ordinary rows, merged scopes, overlapping spans, child changes, rowspan=0, empty rows and empty pages")

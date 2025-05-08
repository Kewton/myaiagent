#!/usr/bin/env node
/**
 * graphaibuilder  – Mermaid flowchart → GraphAI YAML
 * 追加ルール
 *   • inputs キー = <srcNode>_<edgeLabel>（重複防止）
 *   • ラベル無しは <srcNode>
 *   • source を先頭、result* を末尾に
 *   • result* には isResult: true
 */

import fs from "fs";
import path from "path";
import yaml from "js-yaml";

/* ---------- 正規表現 ---------- */
const NODE_DECL = /^\s*([\w-]+)\s*\[\s*"([^"]+)"\s*]\s*$/;
const ARROW = /-[-.]>/;
const QUOTE = /^["'](.*)["']$/;

/* ---------- 型定義 ---------- */
type Edge = [string, string, string];
type NodesDict = Record<string, any>;

/* ---------- 解析 ---------- */
function parseMermaid(text: string): { id2label: Record<string, string>; edges: Edge[] } {
  const id2label: Record<string, string> = {};
  const edges: Edge[] = [];

  for (const line of text.split(/\r?\n/)) {
    const ln = line.trim();
    if (!ln || ln.startsWith("%%") || /^(flowchart|subgraph|end|%%{)/.test(ln)) continue;

    const nodeMatch = NODE_DECL.exec(ln);
    if (nodeMatch) {
      const [, rawId, label] = nodeMatch;
      id2label[rawId] = label;
      continue;
    }

    if (ARROW.test(ln)) {
      const [lhs, tgtRaw] = ln.split(ARROW, 2);
      let tgt = tgtRaw.trim().replace(/;$/, "");
      let src: string, lbl: string;
      if (lhs.includes("--")) {
        [src, lbl] = lhs.split("--", 2).map(s => s.trim());
      } else if (lhs.includes("-.")) {
        [src, lbl] = lhs.split("-.", 2).map(s => s.trim());
      } else {
        src = lhs.trim();
        lbl = "";
      }
      lbl = lbl.replace(QUOTE, "$1");
      edges.push([src, lbl, tgt]);
    }
  }
  return { id2label, edges };
}

/* ---------- 変換 ---------- */
export function mermaidToYaml(mmd: string): string {
  const { id2label, edges } = parseMermaid(mmd);

  const nodes: NodesDict = {};
  const alias: Record<string, string> = {};

  /* ID -> Canonical 名決定 */
  const allIds = new Set<string>([
    ...edges.map(e => e[0]),
    ...edges.map(e => e[2]),
    ...Object.keys(id2label),
  ]);

  function canonical(raw: string): string {
    const base = id2label[raw] ?? raw;
    if (!(base in nodes)) return base;
    let i = 1;
    while (`${base}_${i}` in nodes) i += 1;
    return `${base}_${i}`;
  }

  allIds.forEach(rid => (alias[rid] = canonical(rid)));

  /* source からのラベル収集 */
  const sourceLabels = new Set(
    edges.filter(([s, l]) => alias[s] === "source" && l).map(e => e[1])
  );

  /* エッジ処理 */
  for (const [sRaw, lbl, tRaw] of edges) {
    const src = alias[sRaw];
    const tgt = alias[tRaw];

    const keyBase = lbl ? `${src}_${lbl}` : src;
    let key = keyBase;
    let idx = 1;
    while (nodes?.[tgt]?.inputs?.[key]) {
      key = `${keyBase}_${idx++}`;
    }

    const pathStr = `:${src}${lbl ? "." + lbl : ""}`;

    const tgtNode = (nodes[tgt] = nodes[tgt] ?? {});
    tgtNode.agent ??= `TBD_${tgt}Agent`;
    tgtNode.inputs = tgtNode.inputs ?? {};
    tgtNode.inputs[key] = pathStr;

    nodes[src] ??= { value: "TODO" };
  }

  /* source の value 展開 */
  if (nodes.source) {
    nodes.source.value = Object.fromEntries(
      [...(sourceLabels.size ? sourceLabels : ["prompt"])].sort().map(l => [l, "TODO"])
    );
  }

  /* stub と isResult */
  for (const [name, nd] of Object.entries(nodes)) {
    if (nd.agent) {
      nd.console ??= { before: "TODO" };
      nd.params ??= {};
      if (name.toLowerCase().includes("result")) nd.isResult = true;
    }
  }

  /* 並び替え */
  const ordered: NodesDict = {};
  if (nodes.source) {
    ordered.source = nodes.source;
    delete nodes.source;
  }
  for (const [k, v] of Object.entries(nodes)) {
    if (!k.toLowerCase().includes("result")) ordered[k] = v;
  }
  for (const [k, v] of Object.entries(nodes)) {
    if (k.toLowerCase().includes("result")) ordered[k] = v;
  }

  const graph = { version: 0.5, nodes: ordered };
  // return yaml.dump(graph, { sortKeys: false, lineWidth: 4096 });
  let out = yaml.dump(graph, { sortKeys: false, lineWidth: 4096 });
  out = out.replace(/':([^'\n]+)'/g, ":$1");
  return out;
}

/* ---------- CLI ---------- */
/* ---------- CLI ---------- */
function printUsage(): never {
    console.error(`
  Usage:
    node dist/graphaibuilder.js mermaid2yaml -input <in.mmd> [-output <out.yml>]
  
  例:
    node dist/graphaibuilder.js mermaid2yaml -input sample.mmd -output graph.yaml
  `);
    process.exit(1);
  }
  
  function cli() {
    const argv = process.argv.slice(2);
    if (argv[0] !== "mermaid2yaml") printUsage();
  
    let inputPath: string | undefined;
    let outputPath: string | undefined;
  
    for (let i = 1; i < argv.length; i++) {
      const flag = argv[i];
      if (flag === "-input" && argv[i + 1]) {
        inputPath = argv[++i];
      } else if (flag === "-output" && argv[i + 1]) {
        outputPath = argv[++i];
      } else {
        printUsage();
      }
    }
  
    if (!inputPath) printUsage();
  
    /* ---- 変換 ---- */
    const mmdText = fs.readFileSync(path.resolve(inputPath), "utf8");
    const withHeader = mmdText.includes("flowchart")
      ? mmdText
      : `flowchart TD\n${mmdText}`;
    const yamlOut = mermaidToYaml(withHeader);
  
    if (outputPath) {
      fs.writeFileSync(path.resolve(outputPath), yamlOut, "utf8");
    } else {
      // 出力指定が無ければ stdout
      console.log(yamlOut);
    }
  }
  
  if (require.main === module) cli();
  
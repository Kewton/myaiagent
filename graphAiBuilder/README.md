# setup
```bash
cd graphAiBuilder/
npm install
npm run build
```

# edit
## vscode
- Mermaid Graphical Editor

## sample.mmd
```mermaid
flowchart TB
  node_1["source"]
  node_2["result"]
  node_3["const"]
  node_4["getMarkdownAgent"]
  node_5["generateScriptAgent"]
  node_6["buildmp3"]
  node_7["sendmail"]
  node_8["prompt"]
  node_1 --"articleURL"--> node_4
  node_4 --"articleMarkdown"--> node_5
  node_5 --"script"--> node_6
  node_6 --"mp3fileLink"--> node_7
  node_3 --> node_4
  node_3 --> node_5
  node_3 --> node_6
  node_6 --"mp3fileLink"--> node_8
  node_8 --> node_2
  node_1 --"articleURL"--> node_8
```

# exec
```bash
node dist/graphaibuilder.js mermaid2yaml -input sample.mmd -output graph3.yaml
```


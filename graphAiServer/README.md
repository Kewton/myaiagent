```bash
npm init -y
yarn add typescript --dev
yarn add @types/node --dev
npx tsc --init
yarn add graphai @graphai/vanilla ts-node
yarn add express
yarn add @receptron/test_utils
yarn add @graphai/agents
yarn add @graphai/token_bound_string_agent
yarn add @graphai/vanilla_node_agents
yarn add @graphai/agent_filters
```

```bash
node src/app.js
# 動作確認
curl http://localhost:3000/test
```
// src/services/sample.ts (修正版)
import { GraphAI } from "graphai";
import { readGraphaiData} from "@receptron/test_utils";
import * as packages from "@graphai/agents";
import { tokenBoundStringsAgent } from "@graphai/token_bound_string_agent";
import { fileReadAgent, fileWriteAgent, pathUtilsAgent } from "@graphai/vanilla_node_agents";

const agents = {
  ...packages,
  tokenBoundStringsAgent,
  fileReadAgent,
  fileWriteAgent,
  pathUtilsAgent,
};

// Remove unwanted properties like `__esModule` and `module.exports`
const agents_2 = Object.fromEntries(
  Object.entries(agents).filter(([key]) => key !== "__esModule" && key !== "module.exports")
);


export const main = async () => {

  console.log("Available agents:", Object.keys(agents_2));

  try {
    const graph_data = readGraphaiData("/Users/maenokota/share/work/github_kewton/v0.2/myaiagent/graphAiServer/src/graphAIyml/1_hello-httpAgentFilter.yml");
    
    
    console.log("Graph data:", graph_data);
    console.log(JSON.stringify(graph_data, null, 2));
    const graph = new GraphAI(graph_data, agents_2);
    // console.log("---")
    // console.log(graph.graphData)
    graph.injectValue("source", "ドラゴンボールの作者をメールで送信してね");
    // console.log("---")
    // console.log(graph.graphData)

    const result = await graph.run();
    console.log("GraphAI Result:", result);
    return result;
  } catch (error) {
    console.error("Error during GraphAI instantiation or run:", error);
    throw error;
  }
};
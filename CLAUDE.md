# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a multi-language AI agent system consisting of three main components:

### expertAgent (Python/FastAPI)
- **Purpose**: LangGraph-based utility agents, MCP servers, and FastAPI web service
- **Tech Stack**: Python, FastAPI, LangGraph, MCP (Model Context Protocol)
- **Location**: `expertAgent/`
- **Key Features**:
  - AI agent implementations using LangGraph
  - Google APIs integration (Gmail, Drive)
  - Specialized tools for content generation
  - MCP server implementations for tool interactions

### graphAiServer (Node.js/Express)
- **Purpose**: GraphAI-based workflow execution server
- **Tech Stack**: Node.js, Express, TypeScript, GraphAI
- **Location**: `graphAiServer/`
- **Key Features**:
  - GraphAI workflow processing
  - Integration with multiple LLM providers (OpenAI, Anthropic, Gemini)
  - Express-based REST API

### mlxtest (Python/FastAPI)
- **Purpose**: Local LLM inference server using MLX framework
- **Tech Stack**: Python, FastAPI, MLX-LM
- **Location**: `mlxtest/`
- **Key Features**:
  - Local LLM inference using Apple MLX framework
  - Batch processing for improved throughput
  - OpenAI-compatible API endpoints
  - Support for various quantized models (4-bit, 8-bit)

## Development Commands

### expertAgent Setup and Execution
```bash
cd expertAgent
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run production server
uvicorn app.main:app --workers 5
```

### graphAiServer Setup and Execution
```bash
cd graphAiServer
yarn install

# Run server
NODE_OPTIONS="--loader ts-node/esm" npx ts-node src/app.js
```

### mlxtest Setup and Execution
```bash
cd mlxtest
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run server
uvicorn server:app --host 0.0.0.0 --port 8080 --loop uvloop --workers 4
```

### GraphAI CLI
Global GraphAI CLI tool for workflow execution:
```bash
sudo npm i -g @receptron/graphai_cli
```

## Environment Configuration

### expertAgent (.env)
```
OPENAI_API_KEY=<key>
GOOGLE_API_KEY=<key>
ANTHROPIC_API_KEY=<key>
GOOGLE_APIS_TOKEN_PATH=./token/token.json
GOOGLE_APIS_CREDENTIALS_PATH=./token/credentials.json
MAIL_TO=<email>
LOG_DIR=./log
LOG_LEVEL=INFO
PODCAST_SCRIPT_DEFAULT_MODEL=gpt-4o-mini
SPREADSHEET_ID=<id>
GRAPH_AGENT_MODEL=gpt-4o-mini
OLLAMA_URL=http://localhost:11434
OLLAMA_DEF_SMALL_MODEL=gemma3:27b-it-q8_0
EXTRACT_KNOWLEDGE_MODEL=gemma3:27b-it-q8_0
MLX_LLM_SERVER_URL=http://localhost:8080
```

### graphAI (.env)
```
OPENAI_API_KEY=<key>
GOOGLE_GENAI_API_KEY=<key>
CLAUDE_API_KEY=<key>
```

### mlxtest Environment Variables
```
MODEL_DIR=mlx-community/gemma-3-4b-it-qat-4bit
GPU_SLOTS=5
BATCH_MAX_SIZE=5
BATCH_TIMEOUT_SECONDS=1.5
VERBOSE=False
```

## API Endpoints

### expertAgent (Port 8000)
- Base URL: `http://127.0.0.1:8000/aiagent-api/v1/`
- Sample endpoint: `POST /aiagent-api/v1/aiagent/sample`

### graphAiServer (Port 3030)
- Base URL: `http://localhost:3030/`
- Sample endpoint: `POST /agent/sample/`

### mlxtest (Port 8080)
- OpenAI-compatible completions: `POST /v1/completions`
- OpenAI-compatible chat: `POST /v1/chat/completions`

## Key Dependencies

### expertAgent
- ffmpeg (required for audio processing)
- Google APIs credentials for Gmail/Drive integration
- Various LLM provider API keys

### graphAiServer
- Node.js with TypeScript support
- GraphAI ecosystem packages

### mlxtest
- Apple MLX framework (Mac only)
- Various quantized models from HuggingFace

## Performance Tuning Notes

The mlxtest server includes extensive performance benchmarking data in README.md showing optimal configurations for different model sizes and worker counts. Key parameters for tuning:
- `GPU_SLOTS`: Number of concurrent GPU slots
- `BATCH_MAX_SIZE`: Maximum requests per batch
- `BATCH_TIMEOUT_SECONDS`: Batch processing timeout
- Worker count in uvicorn command

## Model Support

mlxtest supports various quantized models optimized for Apple Silicon:
- gemma-3-4b-it-qat-4bit (recommended for balance of speed/quality)
- gemma-3-12b-it-4bit-DWQ (higher quality, slower)
- Qwen3-8B-4bit (alternative option)
- Various other quantization levels (4-bit, 8-bit)
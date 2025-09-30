import os
from dotenv import load_dotenv  # 追加
import asyncio
import time
import uuid
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Tuple, Any # Tuple, Any を追加
from pydantic import BaseModel, Field
from mlx_lm import load as load_model, generate as generate_once
from mlx_lm.sample_utils import make_sampler


load_dotenv()  # .envファイルを読み込む


# --- 設定値 ---
MODEL_DIR = os.environ.get("MODEL_DIR", "mlx-community/gemma-3-4b-it-qat-4bit")
print(f"Loading model from {MODEL_DIR}...")
GPU_SLOTS = int(os.environ.get("GPU_SLOTS", 5))
BATCH_MAX_SIZE = int(os.environ.get("BATCH_MAX_SIZE", 5))
BATCH_TIMEOUT_SECONDS = float(os.environ.get("BATCH_TIMEOUT_SECONDS", 1.5))
VERBOSE = os.environ.get("VERBOSE", "False").lower() in ("1", "true", "yes")


# --- グローバル変数 ---
model, tokenizer = load_model(MODEL_DIR)
model.eval()

app = FastAPI(title="MLX-LM API (async semaphore with batching)")

# 同時生成を抑制するためのセマフォ
sem = asyncio.Semaphore(GPU_SLOTS)

# リクエストキュー（アイテムは (リクエストデータ, Futureオブジェクト, リクエストタイプ文字列) のタプル）
request_queue: asyncio.Queue[Tuple[Any, asyncio.Future, str]] = asyncio.Queue()


# --- Pydanticモデル ---
class ChatReq(BaseModel):
    prompt: str = Field(..., example="こんにちは、自己紹介してください。")
    max_tokens: int = 512
    temperature: float = 0.1


class ChatResp(BaseModel):
    text: str


class OpenAIChatMessage(BaseModel):
    role: str
    content: str


class OpenAIChatRequest(BaseModel):
    messages: List[OpenAIChatMessage]
    model: str = MODEL_DIR
    max_tokens: int = 512
    temperature: float = 0.1


# --- バッチ処理ワーカ ---
async def process_batches():
    """
    キューからリクエストをまとめて取り出し、バッチで処理するワーカ。
    """
    while True:
        gathered_items: List[Tuple[Any, asyncio.Future, str]] = []
        batch_start_time = time.monotonic()

        # バッチサイズまたはタイムアウトまでアイテムを収集
        while len(gathered_items) < BATCH_MAX_SIZE:
            try:
                # 残り時間を計算してタイムアウトを設定
                remaining_timeout = BATCH_TIMEOUT_SECONDS - (time.monotonic() - batch_start_time)
                if remaining_timeout <= 0:  # タイムアウト
                    if len(gathered_items) > 0:  # 既にアイテムがあれば処理へ
                        break
                    else:  # アイテムがなければ次のポーリングサイクルへ (0.01秒待つ)
                        await asyncio.sleep(0.01)  # CPU負荷軽減のための短いスリープ
                        batch_start_time = time.monotonic()  # タイムアウト開始時間をリセット
                        continue

                # キューからアイテムをタイムアウト付きで取得
                req_data, future, req_type = await asyncio.wait_for(
                    request_queue.get(),
                    timeout=max(0.001, remaining_timeout)  # ゼロ以下のタイムアウトを避ける
                )
                gathered_items.append((req_data, future, req_type))
                request_queue.task_done()
            except asyncio.TimeoutError:
                # タイムアウトしたが、既にアイテムがあればバッチ処理へ
                if len(gathered_items) > 0:
                    break
                # タイムアウトしてアイテムもなければループの先頭に戻り、再度収集を試みる
            except Exception as e:
                print(f"Error in batch worker queue retrieval: {e}")
                # エラーが発生した場合、現在収集中のアイテムのFutureにエラーをセットすることも検討できる
                # ここでは単純に次の処理サイクルへ
                break  # ループを抜けて、もしアイテムがあれば処理、なければ再度キュー監視

        if not gathered_items:
            continue
        # バッチごとのリクエスト数を出力
        batch_size = len(gathered_items)
        print(f"バッチ実績: {batch_size} 件のリクエストを処理します")

        # バッチ処理開始時刻
        batch_process_start = time.monotonic()
        # --- 推論処理 ---
        # mlx_lm.generate_once がバッチ入力をサポートしていない前提で、
        # バッチ内のリクエストを一つずつ逐次処理する。
        llm_times = []
        for req_data, future, req_type in gathered_items:
            if future.done():  # 他の経路で既に処理済み（例：クライアント側タイムアウト）の場合はスキップ
                continue
            try:
                async with sem:  # GPUスロットを確保
                    loop = asyncio.get_running_loop()

                    current_prompt: str
                    current_max_tokens: int
                    current_temperature: float

                    if req_type == "completions":
                        assert isinstance(req_data, ChatReq)
                        current_prompt = req_data.prompt
                        current_max_tokens = req_data.max_tokens
                        current_temperature = req_data.temperature
                    elif req_type == "chat_completions":
                        assert isinstance(req_data, OpenAIChatRequest)
                        current_prompt = req_data.messages[-1].content
                        current_max_tokens = req_data.max_tokens
                        current_temperature = req_data.temperature
                    else: # 未知のリクエストタイプ
                        raise ValueError(f"Unknown request type: {req_type}")

                    sampler = make_sampler(temp=current_temperature)
                    # LLM実行時間の計測開始
                    llm_start = time.monotonic()
                    text_result = await loop.run_in_executor(
                        None,  # デフォルトのスレッドプールエグゼキュータを使用
                        lambda: generate_once(
                            model,
                            tokenizer,
                            prompt=current_prompt,
                            max_tokens=current_max_tokens,
                            sampler=sampler,
                            verbose=VERBOSE  # デバッグ用に詳細情報を出す場合
                        ),
                    )
                    llm_elapsed = time.monotonic() - llm_start
                    llm_times.append(llm_elapsed)
                    if llm_elapsed >= 60:
                        print(f"LLM実行が60秒以上かかりました。current_prompt: {current_prompt}")
                    if "javascript" in text_result or "JavaScript" in text_result:
                        print(f"JavaScriptから開始しています。current_prompt: {current_prompt}")
                # 結果をFutureにセット
                if req_type == "completions":
                    future.set_result(ChatResp(text=text_result))
                elif req_type == "chat_completions":
                    assert isinstance(req_data, OpenAIChatRequest)
                    response_payload = {
                        "id": f"chatcmpl-{uuid.uuid4().hex}",
                        "object": "chat.completion",
                        "created": int(time.time()),
                        "model": req_data.model,  # リクエストで指定されたモデル名を使用
                        "choices": [
                            {
                                "index": 0,
                                "message": {"role": "assistant", "content": text_result},
                                "finish_reason": "stop",
                            }
                        ],
                        "usage": {
                            "prompt_tokens": None,  # mlx_lmから直接取得は困難
                            "completion_tokens": None,
                            "total_tokens": None,
                        },
                    }
                    future.set_result(response_payload)

            except Exception as e:
                print(f"Error during inference for a request: {e}")
                if not future.done():
                    future.set_exception(e)
    
        # バッチ全体の処理時間
        batch_process_elapsed = time.monotonic() - batch_process_start
        print(f"バッチサイズ: {batch_size}件, バッチ全体の処理時間: {batch_process_elapsed:.3f}秒, 各LLM実行時間: {[f'{t:.3f}' for t in llm_times]}")


# --- FastAPIイベントハンドラ ---
@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時にバッチ処理ワーカを起動"""
    asyncio.create_task(process_batches())
    print(f"Batch processing worker started. Batch_size={BATCH_MAX_SIZE}, Batch_timeout={BATCH_TIMEOUT_SECONDS}s")


# --- APIエンドポイント ---
async def _queue_request_and_wait(request_data: Any, request_type: str):
    """リクエストをキューに追加し、結果を待つ共通ロジック"""
    start_time = time.monotonic()  # 計測開始
    future = asyncio.get_running_loop().create_future()
    try:
        await request_queue.put((request_data, future, request_type))
        response_data = await future
        return response_data
    except asyncio.CancelledError:
        print("Request was cancelled by client.")
        raise HTTPException(status_code=499, detail="Client Closed Request")
    except Exception as e:
        print(f"Error in queuing request or awaiting future: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        elapsed = time.monotonic() - start_time
        print(f"_queue_request_and_wait elapsed: {elapsed:.3f}秒")


@app.post("/v1/completions", response_model=ChatResp)
async def completions_endpoint(req: ChatReq):
    """
    通常のリクエストを受け付け、キューに追加するエンドポイント。
    """
    return await _queue_request_and_wait(req, "completions")


@app.post("/v1/chat/completions", response_model=Dict[str, Any]) # OpenAI互換なのでDict[str, Any]
async def chat_completions_endpoint(req: OpenAIChatRequest):
    """
    OpenAI Chat Completions 風インターフェース（stream 未対応）。
    """
    print("-- start --")
    if not req.messages:  # Pydanticで必須だが念のため
        raise HTTPException(status_code=400, detail="messages is required")
    return await _queue_request_and_wait(req, "chat_completions")

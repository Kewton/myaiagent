from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from aiagent.tool.google_search_by_gemini import google_search_tool
from aiagent.tool.tts_and_upload_drive import TextToSpeechAndUploadTool
from aiagent.googleapis import gmail_search_search_tool, SendEmailTool
import os
from aiagent.aiagent.base import AiAgentBase
from aiagent.aiagent.common import isChatGPTImageAPI, isGemini


tts_upload_tool = TextToSpeechAndUploadTool()
send_email_tool = SendEmailTool()


class StandardAiAgent(AiAgentBase):
    # デフォルト値をクラス変数として定義
    DEFAULT_MODEL = "gemini-1.5-pro"
    DEFAULT_MAX_ITERATIONS = 5
    DEFAULT_MAX_TOOLS = [
            google_search_tool,
            send_email_tool,
            gmail_search_search_tool,
            tts_upload_tool
    ]

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        verbose: bool = True,
        tools: list = DEFAULT_MAX_TOOLS,
        return_intermediate_steps: bool = True
    ):
        """
        agenttype2 のコンストラクタ。

        Args:
            model_name (str): 使用するLLMモデル名。
            max_iterations (int): AgentExecutorの最大反復回数。
            verbose (bool): 詳細ログ出力を行うか。
            return_intermediate_steps (bool): 中間ステップを返すか。
        """
        # インスタンス変数を設定
        self.model_name = model_name if model_name is not None else self.DEFAULT_MODEL
        self.max_iterations = max_iterations if max_iterations is not None else self.DEFAULT_MAX_ITERATIONS
        self.verbose = verbose
        self.return_intermediate_steps = return_intermediate_steps
        self.tools = tools
        self.model = self.__createllm()

        super().__init__()

    def __createllm(self):
        if isChatGPTImageAPI(self.model_name):
            # APIキーの存在チェック (環境変数から取得)
            if not os.environ.get("OPENAI_API_KEY"):
                raise ValueError("Environment variable 'OPENAI_API_KEY' is not set.")
            try:
                return ChatOpenAI(model=self.model_name)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize ChatOpenAI with model '{self.model_name}': {e}")
        elif isGemini(self.model_name):
            # APIキーの存在チェック (環境変数から取得)
            self.api_key = os.environ.get("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("Environment variable 'GEMINI_API_KEY' is not set.")
            try:
                # gemini-1.5-pro
                # gemini-2.5-pro-exp-03-25

                return ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key
                )
            except Exception as e:
                raise RuntimeError(f"Failed to initialize ChatGoogleGenerativeAI with model '{self.model_name}': {e}")

    # 2. createAgentExecutor でインスタンス変数を使用
    def createAgentExecutor(self) -> AgentExecutor:
        """AgentExecutor を生成して返します。"""
        # print(f"Creating AgentExecutor with model={self.model_name}, max_iter={self.max_iterations}") # デバッグ用
        # HubからReact用プロンプトを取得
        try:
            prompt = hub.pull("hwchase17/react")
        except Exception as e:
            raise RuntimeError(f"Failed to pull prompt from hub: {e}")

        # エージェントの作成
        try:
            agent = create_react_agent(self.model, self.tools, prompt)
        except Exception as e:
            raise RuntimeError(f"Failed to create react agent: {e}")

        # AgentExecutor の実行準備：インスタンス変数を使用
        try:
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=self.verbose,
                handle_parsing_errors=True,
                max_iterations=self.max_iterations,
                return_intermediate_steps=self.return_intermediate_steps
            )
            return agent_executor
        except Exception as e:
            raise RuntimeError(f"Failed to create AgentExecutor: {e}")

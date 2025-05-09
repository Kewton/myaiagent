import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

llm_openai = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


async def jsonOutputagent(query: str):
    outline_json = (await llm_openai.ainvoke(query)).content
    print("~~~~ outline_json [start]~~~~")
    print(outline_json)
    print("~~~~ outline_json [end]~~~~")

    parser = JsonOutputParser()
    try:
        parsed_json = parser.parse(outline_json)
    except Exception as e:
        print(f"Error parsing JSON with JsonOutputParser: {e}")
        # --- (または、正規表現を使用する場合) ---
        match = re.search(r"```json\s*(\{.*?\})\s*```", outline_json, re.DOTALL)
        if match:
            json_content = match.group(1)
            try:
                parsed_json = json.loads(json_content)
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError after regex extraction: {e}")
                raise
            except KeyError as e:
                print(f"KeyError: {e}. 'outline' key not found.")
                raise
        else:
            print("Could not extract JSON block using regex.")
            # JSONブロックが見つからない場合のエラーハンドリング
            raise ValueError("Failed to extract JSON block from LLM response.")

    return parsed_json

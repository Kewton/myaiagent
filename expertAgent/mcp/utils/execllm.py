from openai import OpenAI
import google.generativeai as genai
import os


chatgptapi_client = OpenAI(
  api_key=os.environ.get("OPENAI_API_KEY")
)


genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


def isChatGptAPI(_selected_model):
    if "gpt" in _selected_model:
        return True
    else:
        return False


def isChatGPT_o(_selected_model):
    if "o1" in _selected_model:
        return True
    elif "o3" in _selected_model:
        return True
    else:
        return False


def isChatGPTImageAPI(_selected_model):
    if "gpt-4o" in _selected_model:
        return True
    elif "o1" in _selected_model:
        return True
    elif "o3" in _selected_model:
        return True
    else:
        return False


def isGemini(_selected_model):
    if "gemini" in _selected_model:
        return True
    else:
        return False


def buildInpurtMessages(_messages, encoded_file):
    _inpurt_messages = []
    _systemrole = ""
    for _rec in _messages:
        if _rec["role"] == "system":
            _systemrole = _rec["content"]
        elif _rec["role"] == "user":
            if len(encoded_file) > 0:
                print("append image")
                _content = []
                _content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": encoded_file
                    }
                })
                _content.append({
                    "type": "text",
                    "text": _rec["content"]
                })

                _inpurt_messages.append(
                    {
                        "role": _rec["role"],
                        "content": _content
                    }
                )
            else:
                _inpurt_messages.append(_rec)

    return _inpurt_messages, _systemrole


def buildInpurtMessagesForGemini(_messages):
    system_instruction = None
    contents_for_api = []

    for msg in _messages:
        role = msg.get("role")
        content = msg.get("content")
        if not role or not content:
            continue

        if role == "system":
            system_instruction = content
        elif role == "user":
            # 正しい形式: 'parts' キーの中に {'text': ...} のリストを入れる
            contents_for_api.append({'role': 'user', 'parts': [{'text': content}]})
        elif role == "assistant" or role == "model":
            # 正しい形式: 'parts' キーの中に {'text': ...} のリストを入れる
            contents_for_api.append({'role': 'model', 'parts': [{'text': content}]})

    return contents_for_api, system_instruction


def execLlmApi(_selected_model, _messages, encoded_file=""):
    if isChatGptAPI(_selected_model):
        if isChatGPTImageAPI(_selected_model) and len(encoded_file) > 0:
            _inpurt_messages = []
            _inpurt_messages.append(_messages[0])
            _inpurt_messages.append(
                {"role": "user", "content": [
                    {"type": "text", "text": _messages[1]["content"]},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_file}"}}
                ]}
            )
            response = chatgptapi_client.chat.completions.create(
                model=_selected_model,
                messages=_inpurt_messages
            )
        else:
            response = chatgptapi_client.chat.completions.create(
                model=_selected_model,
                messages=_messages
            )
        return response.choices[0].message.content

    elif isChatGPT_o(_selected_model):
        # ToDo
        #_inpurt_messages, _systemrole = buildInpurtMessages(_messages, encoded_file)
        response = chatgptapi_client.chat.completions.create(
            model=_selected_model,
            messages=_messages
        )

        return response.choices[0].message.content

    elif isGemini(_selected_model):
        _inpurt_messages, _systemrole = buildInpurtMessagesForGemini(_messages)

        # モデル名を有効なものにすること！ (例: "gemini-1.5-flash-latest")
        model = genai.GenerativeModel(
            model_name=_selected_model,  # ★★★ モデル名を有効なものに！ ★★★
            system_instruction=_systemrole,
        )
        response = model.generate_content(_inpurt_messages)
        print("@@@@@@@@@@@")
        print(response.text)
        return response.text

    else:
        return {}

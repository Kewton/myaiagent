from openai import OpenAI
from google import genai
import os


chatgptapi_client = OpenAI(
  api_key=os.environ.get("OPENAI_API_KEY")
)


gemini_client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
)


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
        #_inpurt_messages, _systemrole = buildInpurtMessages(_messages, encoded_file)

        response = chatgptapi_client.chat.completions.create(
            model=_selected_model,
            messages=_messages
        )

        return response.choices[0].message.content

    elif isGemini(_selected_model):
        #_inpurt_messages, _systemrole = buildInpurtMessages(_messages, encoded_file)
        print(_messages)
        response = gemini_client.models.generate_content(
            model=_selected_model,
            contents=_messages
        )
        print("^^^")
        print(response.text,)
        return response.text,

    else:
        return {}

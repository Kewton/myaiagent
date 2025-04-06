#from aiagent.tts.tts import tts
#tts("./test.wav", "あんぱんとは誰か？")

from aiagent.tool.tts_and_upload_drive import tts_and_upload_drive

text_input = """
2025年4月7日 葛飾区 天気\nObservation: 2025年4月7日（月）の葛飾区の天気は、曇り時々晴れです。最高気温は20℃、最低気温は11℃と予想されています。降水確率は午前中が30%、午後が20%です。
"""

print(tts_and_upload_drive("あんぱんmann2", text_input))

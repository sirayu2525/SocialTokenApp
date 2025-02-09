import openai
import os

# OpenAIのAPIキーを設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


text = '''以下のソースコードを基準とします。
a = 0
b = 0
def plus(a,b):
    return a+b

このソースコードの開発にかかるコストを1.00Cと定義します。

では、以下のコードの開発には何Cかかるか算出してください。

a = 1+5
b = 6+7
print(a+b)

なお、返すテキストはかかるコスト(小数点第2位まで記載)です
また、コストの理由も100字以内で説明しなさい
'''



# GPT-3.5-Turboモデルに送信するメッセージ形式を修正
response = openai.ChatCompletion.create(
    model="gpt-4o-mini",  # または gpt-4 など
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": text}
    ]
)

# GPTの返答を取得
gpt_reply = response['choices'][0]['message']['content']
print("ChatGPT:", gpt_reply)

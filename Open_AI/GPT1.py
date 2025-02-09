import openai
import os

# APIキーの設定（自分のAPIキーに置き換えてください）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# チャットモデル用にメッセージを設定
messages = [
    #{"role": "system", "content": "あなたは優秀なプログラマーです。"},
    {"role": "user", "content": "Pythonで足し算をする関数を生成してください。"}
]

# チャットモデルを呼び出し
response = openai.ChatCompletion.create(
    model="gpt-4o-mini",  # 使用するモデル
    messages=messages,  # 入力となるメッセージ
    max_tokens=1000,  # 最大トークン数
    temperature=0.7,  # ランダム性の度合い
    top_p=0.9,  # 確率分布
    frequency_penalty=0.0,  # 頻度ペナルティ
    presence_penalty=0.0,  # 存在ペナルティ
    stop=["\n"]  # 終了トークン
)

# レスポンスの表示
print(response['choices'])

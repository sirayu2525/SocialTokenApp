import os
import requests
import webbrowser
import tkinter as tk
from tkinter import messagebox
from flask import Flask, redirect, request
from threading import Thread

# DiscordのクライアントID, クライアントシークレット、リダイレクトURIを設定
CLIENT_ID = '1338765321116450850'
CLIENT_SECRET = os.getenv("Discord_Oauth2_TOKEN")
REDIRECT_URI = 'http://localhost:5000/callback'
DISCORD_API_URL = 'https://discord.com/api/v10/users/@me'

app = Flask(__name__)

# OAuth2認証のURLを生成
def get_auth_url():
    return f'https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify'

# 認証後のコールバックを処理するエンドポイント
@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return '認証が失敗しました。'

    # Discordのアクセストークンを取得する
    token_url = 'https://discordapp.com/api/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify',
    }

    # トークンをリクエスト
    response = requests.post(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    token_data = response.json()

    print(token_data)
    if 'access_token' in token_data:
        access_token = token_data['access_token']
        # アクセストークンを使ってユーザー情報を取得
        user_response = requests.get(DISCORD_API_URL, headers={'Authorization': f'Bearer {access_token}'})
        user_info = user_response.json()
        return f'認証成功! ユーザー名: {user_info["username"]}'
    else:
        return 'トークン取得に失敗しました。'

# Flaskサーバを別スレッドで実行
def run_flask():
    app.run(debug=True, use_reloader=False, port=5000)

# GUIの作成
class DiscordAuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord OAuth2 認証")

        # 認証ボタン
        self.auth_button = tk.Button(root, text="Discordで認証", command=self.start_auth)
        self.auth_button.pack(pady=20)

        # 結果表示用ラベル
        self.result_label = tk.Label(root, text="", wraplength=300)
        self.result_label.pack(pady=20)

    def start_auth(self):
        # 認証URLを開く
        auth_url = get_auth_url()
        webbrowser.open(auth_url)

        # 結果をGUIに表示
        self.result_label.config(text="ブラウザが開き、Discord認証画面が表示されます。認証後、結果が表示されます。")

# GUIを起動
if __name__ == '__main__':
    # Flaskサーバを別スレッドで実行
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Tkinter GUIの作成
    root = tk.Tk()
    app = DiscordAuthApp(root)
    root.mainloop()

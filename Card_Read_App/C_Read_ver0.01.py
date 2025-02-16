import os
import requests
import webbrowser
import tkinter as tk
from tkinter import messagebox
from flask import Flask, redirect, request
from threading import Thread

import json
import urllib

#https://zenn.dev/3w36zj6/articles/d3894e83cb7423

import Token_Class

import nfc
import binascii

from web3 import Web3

Token_API_url = "http://49.212.162.72/api"
Token_API_key = '1234567890'

TAC = Token_Class.TokenApiClient(Token_API_url, admin_api_key = Token_API_key, timeout = 100)

class DatabaseClient:
    def __init__(self, base_url, api_key):
        """
        :param base_url: APIサーバーのURL (例: "https://localhost")
        :param api_key: アクセス用 API キー
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {"X-API-Key": api_key}

    def create_tables(self, table_name=None):
        params = {}
        if table_name:
            params['table_name'] = table_name
        response = requests.post(
            f"{self.base_url}/create_tables",
            params=params,
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()

    def table_exists(self, table_name):
        response = requests.get(
            f"{self.base_url}/table_exists/{table_name}",
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()

    def add_data(self, table_name, data):
        """
        任意のカラムと値の組み合わせでレコードを挿入する

        :param table_name: テーブル名
        :param data: 挿入するデータ（例: {"col1": "value1", "col2": 123}）
        """
        response = requests.post(
            f"{self.base_url}/data",
            params={'table_name': table_name},
            json=data,
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()

    def get_data_by_field(self, table_name, column, value):
        params = {'table_name': table_name, 'column': column, 'value': value}
        response = requests.get(
            f"{self.base_url}/data/search",
            params=params,
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()
    
    def update_columns(self, table_name, column, search_value, updates):
        """
        指定した条件に合致する行の、複数のカラムを一括更新する。

        :param table_name: 更新するテーブル名
        :param column: 検索対象のカラム名
        :param search_value: 検索する値
        :param updates: 更新するカラム名と新しい値の辞書（例: {"col1": "new_value1", "col2": "new_value2"}）
        :return: 更新後のデータ（辞書形式）
        """
        # updatesをJSON形式の文字列に変換してURLエンコード
        updates_json = json.dumps(updates)
        encoded_updates = urllib.parse.quote(updates_json)
        params = {
            'table_name': table_name,
            'column': column,
            'search_value': search_value,
            'updates': encoded_updates  # updatesをJSON形式の文字列に変換
        }

        # GETリクエストでクエリパラメータとして送信
        response = requests.get(
            f"{self.base_url}/data/update_columns",
            params=params,
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()

database_url = "http://49.212.162.72/db"  # 必要に応じてホスト名/ポートを調整
DB_api_key = "mysecretkey"

DB_client = DatabaseClient(database_url, DB_api_key)
table_name = "data_records"

# DiscordのクライアントID, クライアントシークレット、リダイレクトURIを設定
CLIENT_ID = '1338765321116450850'
CLIENT_SECRET = os.getenv("Discord_Oauth2_TOKEN")
REDIRECT_URI = 'http://localhost:5000/callback'
DISCORD_API_URL = 'https://discord.com/api/v10/users/@me'

flask_app = Flask(__name__)

# OAuth2認証のURLを生成
def get_auth_url():
    return f'https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify'



# GUIの作成
class DiscordAuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord OAuth2 認証")

        self.touch_flag = False
        self.IDm = ''

        # 認証ボタン
        self.auth_button = tk.Button(root, text="Discordと情報をリンク", command=self.start_auth)
        self.auth_button.pack(pady=10)

        # 照会ボタン
        self.inquiry_button = tk.Button(root, text="情報照会", command=self.start_inquiry)
        self.inquiry_button.pack(pady=10)

        # 結果表示用ラベル
        self.result_label = tk.Label(root, text="", wraplength=300, font=("Arial", 18))
        self.result_label.pack(pady=20)

    def start_inquiry(self):
        self.touch_flag = True
        with nfc.ContactlessFrontend("usb") as clf:
            clf.connect(rdwr={"on-connect": self.on_connect})
        found = DB_client.get_data_by_field(table_name, "card_IDm", self.IDm)
        if found == None:
            self.result_label.config(text='そのカードは登録されていません')
            return {'status':'error','code':'not register'}
        else:
            wallet_result = TAC.get_wallet_balance(found['wallet_id'])
            #token_amount = Web3.from_wei(wallet_result['wallet_balance'], "ether")
            self.result_label.config(text='【ユーザー名】\n'+found['discord_name']+'\n【トークン量】\n'+str(wallet_result['wallet_balance'])+' MOP')
            return {'status':'success'}
    
    def start_auth(self):
        # 認証URLを開く
        auth_url = get_auth_url()
        webbrowser.open(auth_url)

        # 結果をGUIに表示
        self.result_label.config(text="認証用画面が開かれます。\n認証が完了したらブラウザの該当タブを閉じて問題ありません。")

    def on_connect(self, tag: nfc.tag.Tag) -> bool:
        try:
            print("connected")
            tag_data = tag.dump()
            print(tag_data)
            #print(tag_data[3].split('|')[1])
            #print(tag_data[7].split('|')[1])
            print("\n".join(tag_data))
            idm = binascii.hexlify(tag._nfcid)
            print("IDm : " + str(idm.decode()))
            self.IDm = str(idm.decode())
            self.touch_flag = False
        except:
            print('::ERROR::')

        return True  # Trueを返しておくとタグが存在しなくなるまで待機され、離すとon_releaseが発火する

    def on_release(self, tag: nfc.tag.Tag) -> None:
        print("released")
        self.touch_flag = False

    def link_user(self,user_name):
        print('Flag_0000')
        found = DB_client.get_data_by_field(table_name, "discord_name", user_name)
        if found == None:
            print('Flag_0001')
            return {'status':'error','code':'Account_Not_Found'}
        else:
            print('Flag_0002')
            self.touch_flag = True
            print('Start_Card_Read【Link_User】')
            with nfc.ContactlessFrontend("usb") as clf:
                #while self.touch_flag:
                clf.connect(rdwr={"on-connect": self.on_connect})#, "on-release": self.on_release})
            print('【Link_User】カード読み込み')
            updated = DB_client.update_columns(table_name,
                                          "discord_name", user_name, 
                                          {"card_IDm": self.IDm})
            self.result_label.config(text='【リンク完了】\nアカウント名：'+user_name)
            return {'status':'success'}
        




# Tkinter GUIの作成
root = tk.Tk()
root.title('Discord情報照会')
root.geometry("400x300")
app = DiscordAuthApp(root)


# 認証後のコールバックを処理するエンドポイント
@flask_app.route('/callback')
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
        print('REQUEST!!')
        user_response = requests.get(DISCORD_API_URL, headers={'Authorization': f'Bearer {access_token}'})
        user_info = user_response.json()
        print(user_info)
        link_info_thread = Thread(target=app.link_user,args=(user_info["username"],))
        link_info_thread.start()
        #app.link_user(user_info["username"])
        return f'認証成功! ユーザー名: {user_info["username"]}'
    else:
        return 'トークン取得に失敗しました。'

# Flaskサーバを別スレッドで実行
def run_flask():
    flask_app.run(debug=True, use_reloader=False, port=5000)

# Flaskサーバを別スレッドで実行
flask_thread = Thread(target=run_flask)
flask_thread.start()


root.mainloop()


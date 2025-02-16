import os
import requests
import webbrowser
import json
import urllib
import binascii
import threading
from threading import Thread

import pygame.freetype  # 追加

import pygame
from flask import Flask, request
import nfc

from web3 import Web3

# Token_Class のインポート（適宜パス等調整）
import Token_Class

# --------------------
# API・DB クライアントの初期化
# --------------------



Token_API_url = "http://49.212.162.72/api"
Token_API_key = '1234567890'
TAC = Token_Class.TokenApiClient(Token_API_url, admin_api_key=Token_API_key, timeout=100)

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
        updates_json = json.dumps(updates)
        encoded_updates = urllib.parse.quote(updates_json)
        params = {
            'table_name': table_name,
            'column': column,
            'search_value': search_value,
            'updates': encoded_updates
        }
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

# --------------------
# Discord OAuth2 関連設定
# --------------------
CLIENT_ID = '1338765321116450850'
CLIENT_SECRET = os.getenv("Discord_Oauth2_TOKEN")
REDIRECT_URI = 'http://localhost:5000/callback'
DISCORD_API_URL = 'https://discord.com/api/v10/users/@me'

def get_auth_url():
    return f'https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify'

# --------------------
# Flask サーバー（OAuth2 コールバック処理）
# --------------------
flask_app = Flask(__name__)

@flask_app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return '認証が失敗しました。'

    # Discord のアクセストークンを取得
    token_url = 'https://discordapp.com/api/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify',
    }
    response = requests.post(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    token_data = response.json()

    print(token_data)
    if 'access_token' in token_data:
        access_token = token_data['access_token']
        user_response = requests.get(DISCORD_API_URL, headers={'Authorization': f'Bearer {access_token}'})
        user_info = user_response.json()
        print(user_info)
        # Flask から pygame のアプリ（グローバルインスタンス pygame_app）へリンク処理を依頼
        Thread(target=pygame_app.link_user, args=(user_info["username"],)).start()
        return f'認証成功! ユーザー名: {user_info["username"]}'
    else:
        return 'トークン取得に失敗しました。'

def run_flask():
    flask_app.run(debug=True, use_reloader=False, port=5000)

# --------------------
# pygame 用のボタンクラス
# --------------------
class Button:
    def __init__(self, rect, text, callback, font, text_color=(255,255,255), button_color=(70,130,180)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.text_color = text_color
        self.button_color = button_color

    def draw(self, surface):
        # 影の描画（少し右下にずらす）
        shadow_offset = 3
        shadow_rect = self.rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        pygame.draw.rect(surface, (50, 50, 50), shadow_rect, border_radius=8)
        
        # ボタン本体の描画（角丸）
        pygame.draw.rect(surface, self.button_color, self.rect, border_radius=8)
        
        # ボタンの枠線を描画
        pygame.draw.rect(surface, (30, 30, 30), self.rect, width=2, border_radius=8)
        
        # テキストの描画
        text_rect = self.font.get_rect(self.text)
        text_rect.center = self.rect.center
        self.font.render_to(surface, text_rect.topleft, self.text, self.text_color)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# --------------------
# pygame 用 UI アプリクラス
# --------------------
class PygameAuthApp:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        #self.font = pygame.font.SysFont("meiryo", 24)
        #self.result_font = pygame.font.SysFont("meiryo", 24)
        #self.font = pygame.freetype.SysFont("meiryo", 24)
        #self.result_font = pygame.freetype.SysFont("meiryo", 24)
        self.font = pygame.freetype.SysFont("meiryo", 24)
        self.result_font = pygame.freetype.SysFont("meiryo", 24, bold = True)
        #self.font.bold = True
        #self.result_font.bold = True
        self.result_message = ""
        self.touch_flag = False
        self.IDm = ""

        # ボタンのサイズ・配置設定
        button_width = 300
        button_height = 50
        spacing = 20
        x = (self.width - button_width) // 2
        y1 = 100
        y2 = y1 + button_height + spacing

        #self.button_auth = Button((x, y1, button_width, button_height), "Discordと情報をリンク", self.handle_auth, self.font)
        self.button_auth = Button((x, y1, button_width, button_height), 
                          "Discordと情報をリンク", 
                          self.handle_auth, 
                          self.font, 
                          text_color=(0, 0, 0), 
                          button_color=(200, 200, 200))
        self.button_inquiry = Button((x, y2, button_width, button_height), "情報照会", self.handle_inquiry, self.font)

    def handle_auth(self):
        # OAuth2 認証用URLをブラウザで開く
        auth_url = get_auth_url()
        webbrowser.open(auth_url)
        self.result_message = "認証用画面が開かれます\n認証完了後、ブラウザを閉じてください"

    def handle_inquiry(self):
        # NFC 読み取り＆情報照会は別スレッドで実行（UIブロック防止）
        Thread(target=self.start_inquiry).start()

    def start_inquiry(self):
        self.touch_flag = True
        try:
            with nfc.ContactlessFrontend("usb") as clf:
                clf.connect(rdwr={"on-connect": self.on_connect})
        except Exception as e:
            print("NFC 読み取りエラー:", e)
        # NFC で取得したカード IDm を使って DB からユーザ情報を取得
        found = DB_client.get_data_by_field(table_name, "card_IDm", self.IDm)
        if found is None:
            self.result_message = 'そのカードは登録されていません'
        else:
            wallet_result = TAC.get_wallet_balance(found['wallet_id'])
            self.result_message = f'【ユーザー名】：{found["discord_name"]}\n【トークン量】：{wallet_result["wallet_balance"]} MOP'

    def on_connect(self, tag: nfc.tag.Tag) -> bool:
        try:
            print("カード接続")
            tag_data = tag.dump()
            print("\n".join(tag_data))
            idm = binascii.hexlify(tag._nfcid)
            self.IDm = idm.decode()
            self.touch_flag = False
        except Exception as e:
            print("on_connect エラー:", e)
        return True

    def link_user(self, user_name):
        # Discord ユーザー名から DB で該当ユーザーを検索し、カードIDを紐付ける
        found = DB_client.get_data_by_field(table_name, "discord_name", user_name)
        if found is None:
            self.result_message = 'アカウントが見つかりません'
            return {'status': 'error', 'code': 'Account_Not_Found'}
        else:
            self.touch_flag = True
            try:
                with nfc.ContactlessFrontend("usb") as clf:
                    clf.connect(rdwr={"on-connect": self.on_connect})
            except Exception as e:
                print("NFC 読み取りエラー（link_user）:", e)
            updated = DB_client.update_columns(table_name,
                                               "discord_name", user_name, 
                                               {"card_IDm": self.IDm})
            self.result_message = f'　　【リンク完了】\nアカウント名：{user_name}'
            return {'status': 'success'}

    def draw_vertical_gradient(self, surface, color_top, color_bottom):
        """画面全体に縦方向のグラデーションを描画する
        :param surface: 描画対象のpygame.Surface
        :param color_top: 上部の色 (R, G, B)
        :param color_bottom: 下部の色 (R, G, B)
        """
        height = surface.get_height()
        width = surface.get_width()
        for y in range(height):
            # yに沿った補間比率を計算
            ratio = y / height
            # 上部と下部の色を補間
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    def render_glow_text(self, text, font, pos, text_color, glow_color, glow_radius):
        # グロー効果の描画
        for dx in range(-glow_radius, glow_radius+1):
            for dy in range(-glow_radius, glow_radius+1):
                font.render_to(self.screen, (pos[0]+dx, pos[1]+dy), text, glow_color)
        # 通常テキストの描画
        font.render_to(self.screen, pos, text, text_color)

    def draw(self):
        # 画面クリア
        self.screen.fill((100, 175, 35))

        # 背景にグラデーションを描画（上部: 薄いブルー、下部: 濃いブルー）
        self.draw_vertical_gradient(self.screen, (150, 200, 255), (50, 100, 200))


        # ボタン描画
        self.button_auth.draw(self.screen)
        self.button_inquiry.draw(self.screen)
        
        # 結果メッセージを改行ごとに分割
        lines = self.result_message.split('\n')
        line_spacing = 10
        y = 250
        line_spacing = 10
        y = 250
        for line in lines:
            text_rect = self.result_font.get_rect(line)
            x = (self.width - text_rect.width) // 2
            pos = (x, y)
            self.result_font.render_to(self.screen, pos, line, (0, 0, 0))
            y += text_rect.height + line_spacing


# --------------------
# pygame 初期化＆メインループ
# --------------------
pygame.init()
screen = pygame.display.set_mode((500, 400))
pygame.display.set_caption("Discord情報照会")

# グローバルにアクセス可能な pygame アプリのインスタンス
pygame_app = PygameAuthApp(screen)

# Flask サーバーを別スレッドで起動
flask_thread = Thread(target=run_flask)
flask_thread.start()

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            if pygame_app.button_auth.is_clicked(pos):
                pygame_app.handle_auth()
            elif pygame_app.button_inquiry.is_clicked(pos):
                pygame_app.handle_inquiry()

    pygame_app.draw()
    pygame.display.flip()
    clock.tick(30)

pygame.quit()

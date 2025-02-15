import discord
from discord import app_commands
import os

import openai
import requests
import json
import Contract_Operation as CO
import web3

import time
import hashlib

import urllib3

import Token_Class

# 自己署名証明書の警告を無効化（開発環境のみ）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        params = {
            'table_name': table_name,
            'column': column,
            'search_value': search_value
        }
        response = requests.put(
            f"{self.base_url}/data/update_columns",
            params=params,
            json={"updates": updates},  # 辞書を JSON ボディで送信
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()

Token_API_url = "http://49.212.162.72/api"
Token_API_key = 'mysecretkey'

TAC = Token_Class.TokenApiClient(Token_API_url, admin_api_key = Token_API_key, timeout = 100)

database_url = "http://49.212.162.72/db"  # 必要に応じてホスト名/ポートを調整
DB_api_key = "mysecretkey"

DB_client = DatabaseClient(database_url, DB_api_key)
table_name = "data_records"



#import DB_Module

#DBM = DB_Module.DatabaseManager(db_name='user_data.db')

'''
discord_name TEXT PRIMARY KEY,
wallet_id TEXT UNIQUE NOT NULL,
balance REAL DEFAULT 0.0,
github_name TEXT UNIQUE
'''

#if not DBM.table_exists('base_table'):
#    DBM.create_table('base_table','discord_name TEXT PRIMARY KEY,wallet_id TEXT UNIQUE NOT NULL,balance REAL DEFAULT 0.0,github_name TEXT UNIQUE')

# OpenAIのAPIキーを設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def fetch_github_code(url):
    """
    指定されたGitHubのURLからソースコードを取得し、変数に格納する。
    :param url: GitHubのソースコードのURL（raw URL）
    :return: ソースコードの文字列
    """
    try:
        if url.split('/')[2] == 'raw.githubusercontent.com':
            response = requests.get(url)
            response.raise_for_status()  # HTTPエラーが発生した場合は例外を送出
            
            return {'result':True,
                    'text':response.text,
                    'script_type':url.split('.')[-1]}
        else:
            return {'result':False,
                    'code':'Not_Git_Raw'}
    except requests.exceptions.RequestException as e:
        print(f"エラーが発生しました: {e}")
        return {'result':False,
                'code':'Some_Error'}

def evaluate_code(github_raw_url,issue_description):
    # 例: GitHubのraw URLを指定
    #github_raw_url = "https://raw.githubusercontent.com/sirayu2525/SocialTokenApp/refs/heads/evaluation_code/Open_AI/GPT1.py"
    fetch_result = fetch_github_code(github_raw_url)

    if fetch_result['result']:
        source_code = fetch_result['text']

        text = '''以下のソースコードを基準とします。
            def process_data(data):
                return [item for item in data if item >= 10]

            data = [5, 15, 8, 20, 3, 12]
            print("Filtered Data:", process_data(data))

            このソースコードの開発にかかるコストを1.000Cと定義します。

            では、以下のコードの開発には何Cかかるか算出してください。

            '''+source_code+'''

            また、開発してほしいプログラムの概要は以下のようになっています。
            この概要に合致しているかどうかもチェックして合致率(パーセンテージ)で教えてください
            '''+issue_description+'''

            cost:かかるコスト(小数点第2位まで記載して単位は省略)
            reason:コストの理由(100字以内)
            match_percent:合致率(0～100の整数で答えて、単位はつけないでください)
            としたうえで、以下のようなjson形式で答えてください。
            {'cost':cost,'reason':reason,'match_percent':match_percent}
            '''

        if fetch_result['script_type'] == 'py':
            text = '''以下のソースコードを基準とします。
            def process_data(data):
                return [item for item in data if item >= 10]

            data = [5, 15, 8, 20, 3, 12]
            print("Filtered Data:", process_data(data))

            このソースコードの開発にかかるコストを1.000Cと定義します。

            では、以下のコードの開発には何Cかかるか算出してください。

            '''+source_code+'''

            また、開発してほしいプログラムの概要は以下のようになっています。
            この概要に合致しているかどうかもチェックして合致率(パーセンテージ)で教えてください
            '''+issue_description+'''

            cost:かかるコスト(小数点第2位まで記載して単位は省略)
            reason:コストの理由(100字以内)
            match_percent:合致率(0～100の整数で答えて、単位はつけないでください)
            としたうえで、以下のようなjson形式で答えてください。
            {'cost':cost,'reason':reason,'match_percent':match_percent}
            '''
        # GPT-3.5-Turboモデルに送信するメッセージ形式を修正
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # または gpt-4 など
            messages=[
                {"role": "system", "content": "You are a helpful Engineer."},
                {"role": "user", "content": text}
            ]
        )

        # GPTの返答を取得
        gpt_reply = response['choices'][0]['message']['content']
        print("ChatGPT:", gpt_reply)

        gpt_reply = gpt_reply.replace("'''", "")
        gpt_reply = gpt_reply.replace("```", "")
        gpt_reply = gpt_reply.replace("json", "")
        gpt_reply = gpt_reply.replace("'", '"')
        print(gpt_reply)
        # 文字列をJSON形式に変換
        data = json.loads(gpt_reply)
        print(data)

        try:
            gpt_reply = gpt_reply.replace("'''", "")
            gpt_reply = gpt_reply.replace("```", "")
            gpt_reply = gpt_reply.replace("json", "")
            gpt_reply = gpt_reply.replace("'", '"')
            # 文字列をJSON形式に変換
            data = json.loads(gpt_reply)
            print(data)
            return data
        except:
            return None

    else:
        print('【ERROR】')
        print(fetch_result)
        return None



class PJ_Operation:
    def __init__(self):
        # GitHubのAPIエンドポイント
        self.GITHUB_API_URL = "https://api.github.com"
        # あなたのGitHubのユーザー名
        self.USERNAME = "RExIM-cacashi"
        # あなたのGitHub Personal Access Token
        self.TOKEN = os.getenv("GitHub_API_KEY")

        # ヘッダー（認証情報を含む）
        self.headers = {
            "Authorization": f"token {self.TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    def create_repository(self, repo_name, description="自動作成されたリポジトリ", private=False):
        """
        GitHub上に新しいリポジトリを作成する関数
        """
        repo_data = {
            "name": repo_name,
            "description": description,
            "private": private  # True にするとプライベートリポジトリ
        }

        response = requests.post(f"{self.GITHUB_API_URL}/user/repos", json=repo_data, headers=self.headers)

        if response.status_code == 201:
            print(f"リポジトリ '{repo_name}' が作成されました。")
            return True
        else:
            print(f"リポジトリの作成に失敗しました: {response.json()}")
            return False

    def get_URL(self, repo_name):
        repo_url = f"{self.GITHUB_API_URL}/repos/{self.USERNAME}/{repo_name}"
        response = requests.get(repo_url, headers=self.headers)

        if response.status_code == 200:
            repo_info = response.json()
            repo_html_url = repo_info["html_url"]  # リポジトリのURL
            print(f"リポジトリURL: {repo_html_url}")
            return repo_html_url
        else:
            print(f"リポジトリの取得に失敗しました: {response.json()}")
            return None

    def create_issue(self, repo_name, title, body=""):
        """
        指定したリポジトリに新しいIssueを作成する関数
        """
        issue_data = {
            "title": title,
            "body": body
        }

        issue_url = f"{self.GITHUB_API_URL}/repos/{self.USERNAME}/{repo_name}/issues"
        response = requests.post(issue_url, json=issue_data, headers=self.headers)

        if response.status_code == 201:
            print(f"Issue '{title}' が作成されました。")
        else:
            print(f"Issueの作成に失敗しました: {response.json()}")

    def get_issues(self,repo_name):
        """
        指定したリポジトリのIssue一覧を取得する関数
        """
        issue_url = f"{self.GITHUB_API_URL}/repos/{self.USERNAME}/{repo_name}/issues"
        response = requests.get(issue_url, headers=self.headers)

        issue_list = []

        if response.status_code == 200:
            issues = response.json()
            if issues:
                for issue in issues:
                    print(f"Issue #{issue['number']}: {issue['title']}")
                    issue_list.append({'title':issue['title'],'function':issue['body'],'number':issue['number']})
            else:
                print("現在、オープンなIssueはありません。")
        else:
            print(f"Issueの取得に失敗しました: {response.json()}")
        return issue_list

    def close_issue(self, repo_name, issue_number):
        """
        指定したIssueをクローズする関数
        """
        issue_data = {
            "state": "closed"
        }

        issue_url = f"{self.GITHUB_API_URL}/repos/{self.USERNAME}/{repo_name}/issues/{issue_number}"
        response = requests.patch(issue_url, json=issue_data, headers=self.headers)

        if response.status_code == 200:
            print(f"Issue #{issue_number} はクローズされました。")
        else:
            print(f"Issueのクローズに失敗しました: {response.json()}")
    
    def make_PJ(self,PJ_description):
        text = """以下のプロジェクトを遂行するために必要と考えられるコーディングの作業を全て洗い出し、以下の粒度基準に基づいてタスクとしてリストアップしてください
なお、出力形式としては全てjson形式で、それ以外の文章は一切出力しないでください
また、各タスクにはID(数字)を振り、求められる機能も書いてください
さらに、プロジェクト自体の名前も端的に分かりやすく命名(必ず英語で)してください
タスクにおける記述は基本的に日本語で生成してください。
・他のタスクと依存関係が少ない
・PR、テスト可能な単位
・1時間～2日以内で完了する規模
・モジュール単位で分割
・単体の機能として完結
[PJ概要]
"""+PJ_description+"""
[出力形式]
{"tasks":[{'ID':1,'title':"Title",'function':''},......],"PJ_name":"PJ_name"}

('''json等はいらないです)
"""
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

        print(gpt_reply)

        gpt_reply = gpt_reply.replace("'''", "")
        gpt_reply = gpt_reply.replace("```", "")
        gpt_reply = gpt_reply.replace("json", "")
        gpt_reply = gpt_reply.replace("'", '"')
        # 文字列をJSON形式に変換
        data = json.loads(gpt_reply)

        print(data)
        print('PJ_NAME:::'+data['PJ_name'])

        self.create_repository(data['PJ_name'],description=PJ_description)

        issue_list = {'PJ_name':data['PJ_name'],'issue':[]}

        count = 1
        for i in data['tasks']:
            self.create_issue(data['PJ_name'],i['title'],body = i['function'])
            issue_list['issue'].append({'title':i['title'],'function':i['function'],'number':count})
            count += 1
        
        return issue_list

    def invite_user(self, repo_name, INVITE_USER):
        invite_url = f"{self.GITHUB_API_URL}/repos/{self.USERNAME}/{repo_name}/collaborators/{INVITE_USER}"
        invite_response = requests.put(invite_url, headers=self.headers)

        if invite_response.status_code in [201, 204]:
            print(f"{INVITE_USER} さんをリポジトリに招待しました！")
        else:
            print(f"ユーザーの招待に失敗しました: {invite_response.json()}")

    def get_repo_description(self, repo_name):
        """
        指定したリポジトリの description を取得する関数
        :param repo_name: リポジトリ名 (例: "owner/repo")
        :return: リポジトリの description (文字列)
        """
        url = f"{self.GITHUB_API_URL}/repos/{self.USERNAME}/{repo_name}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            repo_data = response.json()
            description = repo_data.get("description", "No description available.")
            print(f"リポジトリ '{repo_name}' の description: {description}")
            return description
        else:
            print(f"リポジトリの description 取得に失敗しました: {response.status_code}, {response.json()}")
            return None

PJO = PJ_Operation()



Disocrd_TOKEN = os.getenv("Discord_Bot_TOKEN")

client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)


@tree.command(name="start_pj",description="PJの作成を行います")
async def test_command(interaction: discord.Interaction,
                        pj_description: str):
    await interaction.response.send_message('PJを作成します',ephemeral=True)

    issue_list = PJO.make_PJ(pj_description)

    embed = discord.Embed(title = '**'+issue_list['PJ_name']+'**', color = 0x00ff00, description = pj_description)
    for i in issue_list['issue']:
        embed.add_field(name = '__#'+str(i['number'])+' ['+i['title']+']__',value = i['function'],inline=False)
    embed.set_footer(text="PJ Task-List")
    
    await interaction.channel.send(embed = embed)


@tree.command(name="get_tasks",description="タスクを取得します")
async def test_command(interaction: discord.Interaction,
                        pj_name: str):
    await interaction.response.send_message('タスクを取得します',ephemeral=True)

    issue_list = PJO.get_issues(pj_name)
    print(PJO.get_repo_description(pj_name))
    PJ_description = PJO.get_repo_description(pj_name)

    embed = discord.Embed(title = '**'+pj_name+'**', color = 0xcc00aa, description = PJ_description)
    for i in issue_list:
        embed.add_field(name = '__#'+str(i['number'])+' ['+i['title']+']__',value = i['function'],inline=False)
    embed.set_footer(text="PJ Task-List")
    
    await interaction.channel.send(embed = embed)


@tree.command(name="complete_task",description="タスク完了申請をします")
async def test_command(interaction: discord.Interaction,
                        pj_name: str,
                        issue_number:int,
                        github_url:str):
    await interaction.response.send_message('タスクの完了申請を開始します',ephemeral=True)

    user_name = interaction.user.name  # アカウント名（ユーザーネーム）を取得
    found = DB_client.get_data_by_field(table_name, "discord_name", user_name)
    if found == None:
        embed = discord.Embed(title = '**リンク情報不備**', color = 0xff4444, description = '')
        embed.add_field(name = '【お願い】',value = 'タスク完了申請を行うためには情報リンクを行ってください',inline=False)
        await interaction.channel.send(embed = embed)
        return
    else:
        wallet_id = found['wallet_id']
    
    issue_list = PJO.get_issues(pj_name)
    for i in issue_list:
        if i['number'] == issue_number:
            evaluate_result = evaluate_code(github_url,i['title']+'\n'+i['function'])
            issue_title = i['title']
            #issue_function = i['function']
            break
    
    embed = discord.Embed(title = '**評価申請**', color = 0xffffff, description = pj_name+'\n'+str(issue_number))
    embed.add_field(name = 'リポジトリー名',value = pj_name,inline=False)
    embed.add_field(name = 'タスクタイトル',value = issue_title,inline=False)
    embed.add_field(name = 'Issue Number',value = issue_number,inline=False)
    embed.add_field(name = '付与トークン',value = str(evaluate_result['cost'])+'MOP',inline=False)
    embed.add_field(name = '評価理由',value = evaluate_result['reason'],inline=False)
    embed.add_field(name = '合致率',value = str(evaluate_result['match_percent']),inline=False)
    embed.add_field(name = '評価対象コード',value = github_url,inline=False)
    
    if int(evaluate_result['match_percent']) >= 60:
        now_hs = hashlib.sha256(str(time.time()).encode()).hexdigest()
        embed.add_field(name = '申請結果',value = '受領',inline=False)
        embed.add_field(name = 'トークン付与コード',value = now_hs,inline=False)
        embed.set_footer(text="申請を受け付けました")
        await interaction.channel.send(embed = embed)

        #wallet_id = "0xd525f542c3F2d16D12dA68578bd69d068A854BD0"
        token_amount = float(evaluate_result['cost'])  # 🔹 10 MOP
        amount_wei = web3.to_wei(token_amount, "ether")

        try:
            print(f"🔹 {wallet_id} に {token_amount} MOP を発行中...")
            mint_response = TAC.mint_tokens(wallet_id, amount_wei)

            if mint_response['status'] == 'Success':

                trade_list = found['tx_hashes']
                trade_list.append(str(mint_response['tx_hash']))

                DB_client.update_columns(table_name, "discord_name", user_name, {'tx_hash':trade_list})

                #new_balance = CO.contract.functions.balanceOf(wallet_id).call()
                #print(f"💰 新しいトークン残高: {web3.from_wei(new_balance, 'ether')} MOP")
                PJO.close_issue(pj_name,issue_number)
                embed = discord.Embed(title = '**トークン付与完了**', color = 0x998800, description = pj_name+'\n'+str(issue_number))
                embed.add_field(name = 'トークン付与コード',value = now_hs,inline=False)
                embed.add_field(name = '送付先',value = wallet_id,inline=False)
                embed.add_field(name = '付与トークン量',value = str(evaluate_result['cost'])+'MOP',inline=False)
                embed.add_field(name = 'tx_hash',value = str(mint_response['tx_hash']),inline=False)
                embed.set_footer(text="トークンを付与しました")
                await interaction.channel.send(embed = embed)
            else:
                embed = discord.Embed(title = '**トークン付与失敗**', color = 0xff0000, description = pj_name+'\n'+str(issue_number))
                embed.add_field(name = '結果',value = 'トークンの付与に失敗しました',inline=False)
                await interaction.channel.send(embed = embed)
                print("❌ トークン発行に失敗しました")

        except Exception as e:
            print(f"❌ エラー: {str(e)}")
    else:
        embed.add_field(name = '申請結果',value = '不受理',inline=False)
        embed.set_footer(text="合致率が基準値を満たさず不受理")
        await interaction.channel.send(embed = embed)


@tree.command(name="link_info",description="リンク情報を更新します")
async def test_command(interaction: discord.Interaction,
                        github_username: str,
                        wallet_id:str):
    await interaction.response.send_message('リンク情報を更新します',ephemeral=True)
    user_name = interaction.user.name  # アカウント名（ユーザーネーム）を取得
    found = DB_client.get_data_by_field(table_name, "discord_name", user_name)
    if found == None:
        updated = DB_client.update_columns(table_name,
                                          "discord_name", user_name, 
                                          {"github_username": github_username, "wallet_id": wallet_id})
        if updated == None:
            embed = discord.Embed(title = '**リンク情報の更新**', color = 0xff4444, description = '')
            embed.add_field(name = '結果',value = '失敗',inline=False)
            await interaction.channel.send(embed = embed)
        else:
            embed = discord.Embed(title = '**リンク情報の更新**', color = 0x44ff44, description = '')
            embed.add_field(name = '結果',value = '成功',inline=False)
            await interaction.channel.send(embed = embed)
    else:
        added = DB_client.add_data(table_name, {"discord_name":user_name, 
                                                "github_username": github_username,
                                                "wallet_id":wallet_id})
        if updated == None:
            embed = discord.Embed(title = '**リンク情報の更新**', color = 0xff4444, description = '')
            embed.add_field(name = '結果',value = '失敗',inline=False)
            await interaction.channel.send(embed = embed)
        else:
            embed = discord.Embed(title = '**リンク情報の更新**', color = 0x44ff44, description = '')
            embed.add_field(name = '結果',value = '成功',inline=False)
            await interaction.channel.send(embed = embed)


'''
id = Column(Integer, primary_key=True, index=True)  # 自動インクリメントの ID
discord_name = Column(String(100), nullable=False)  # Discordアカウント名
github_username = Column(String(100), nullable=False)  # GitHubユーザー名
balance = Column(Integer, default=0)  # 残高（日本円）
wallet_id = Column(String(255), unique=True, nullable=False)  # ウォレットID（文字列）
tx_hashes = Column(JSON, default=[])  # 取引履歴（リスト型）
'''


@tree.command(name="稼働終了",description="Botを停止させる。管理者権限必須")
@app_commands.default_permissions(administrator=True)
async def test_command(interaction:discord.Interaction):
    await interaction.response.send_message("Botを停止します。",ephemeral=True)
    await client.close()




@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await tree.sync()
    print('起動')

    
    


client.run(Disocrd_TOKEN)
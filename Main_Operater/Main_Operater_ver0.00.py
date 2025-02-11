import discord
from discord import app_commands
import os

import openai
import os
import requests
import json

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

def evaluate_code(github_raw_url):
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

            なお、返すテキストはかかるコスト(小数点第2位まで記載)です
            また、コストの理由も100字以内で説明しなさい'''

        if fetch_result['script_type'] == 'py':
            text = '''以下のソースコードを基準とします。
            def process_data(data):
                return [item for item in data if item >= 10]

            data = [5, 15, 8, 20, 3, 12]
            print("Filtered Data:", process_data(data))

            このソースコードの開発にかかるコストを1.000Cと定義します。

            では、以下のコードの開発には何Cかかるか算出してください。

            '''+source_code+'''

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
        return gpt_reply
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
                    issue_list.append({'title':issue['title'],'description':issue['body']})
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

        # 文字列をJSON形式に変換
        data = json.loads(gpt_reply)

        print(data)
        print('PJ_NAME:::'+data['PJ_name'])

        self.create_repository(data['PJ_name'],description=PJ_description)

        issue_list = {'PJ_name':data['PJ_name'],'issue':[]}

        for i in data['tasks']:
            self.create_issue(data['PJ_name'],i['title'],body = i['function'])
            issue_list['issue'].append({'title':i['title'],'function':i['function']})
        
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
        embed.add_field(name = '__'+i['title']+'__',value = i['function'],inline=False)
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
        embed.add_field(name = '__'+i['title']+'__',value = i['description'],inline=False)
    embed.set_footer(text="PJ Task-List")
    
    await interaction.channel.send(embed = embed)



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
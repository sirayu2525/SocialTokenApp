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

        if response.status_code == 200:
            issues = response.json()
            if issues:
                for issue in issues:
                    print(f"Issue #{issue['number']}: {issue['title']}")
            else:
                print("現在、オープンなIssueはありません。")
        else:
            print(f"Issueの取得に失敗しました: {response.json()}")

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

        for i in data['tasks']:
            self.create_issue(data['PJ_name'],i['title'],body = i['function'])

    def invite_user(self, repo_name, INVITE_USER):
        invite_url = f"{self.GITHUB_API_URL}/repos/{self.USERNAME}/{repo_name}/collaborators/{INVITE_USER}"
        invite_response = requests.put(invite_url, headers=self.headers)

        if invite_response.status_code in [201, 204]:
            print(f"{INVITE_USER} さんをリポジトリに招待しました！")
        else:
            print(f"ユーザーの招待に失敗しました: {invite_response.json()}")

PJO = PJ_Operation()
#PJO.make_PJ('競技プログラミングのユーザーの熟練度をAIが判断してスキルアップをしてくれるサービス')

#PJO.get_URL('SkillUpAI')

#PJO.invite_user('SkillUpAI', 'mstka')

#PJO.create_repository('Skill_Up_PJ',description='競技プログラミングのユーザーの熟練度をAIが判断してスキルアップをしてくれるサービス')
#PJO.get_issues('auto-created-repo')
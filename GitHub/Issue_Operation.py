import requests
import os

# GitHubのAPIエンドポイント
GITHUB_API_URL = "https://api.github.com"
# あなたのGitHubのユーザー名
USERNAME = "RExIM-cacashi"
# あなたのGitHub Personal Access Token
TOKEN = os.getenv("GitHub_API_KEY")

# ヘッダー（認証情報を含む）
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def create_repository(repo_name, description="自動作成されたリポジトリ", private=False):
    """
    GitHub上に新しいリポジトリを作成する関数
    """
    repo_data = {
        "name": repo_name,
        "description": description,
        "private": private  # True にするとプライベートリポジトリ
    }

    response = requests.post(f"{GITHUB_API_URL}/user/repos", json=repo_data, headers=headers)

    if response.status_code == 201:
        print(f"リポジトリ '{repo_name}' が作成されました。")
        return True
    else:
        print(f"リポジトリの作成に失敗しました: {response.json()}")
        return False

def create_issue(repo_name, title, body=""):
    """
    指定したリポジトリに新しいIssueを作成する関数
    """
    issue_data = {
        "title": title,
        "body": body
    }

    issue_url = f"{GITHUB_API_URL}/repos/{USERNAME}/{repo_name}/issues"
    response = requests.post(issue_url, json=issue_data, headers=headers)

    if response.status_code == 201:
        print(f"Issue '{title}' が作成されました。")
    else:
        print(f"Issueの作成に失敗しました: {response.json()}")

def get_issues(repo_name):
    """
    指定したリポジトリのIssue一覧を取得する関数
    """
    issue_url = f"{GITHUB_API_URL}/repos/{USERNAME}/{repo_name}/issues"
    response = requests.get(issue_url, headers=headers)

    if response.status_code == 200:
        issues = response.json()
        if issues:
            for issue in issues:
                print(f"Issue #{issue['number']}: {issue['title']}")
        else:
            print("現在、オープンなIssueはありません。")
    else:
        print(f"Issueの取得に失敗しました: {response.json()}")

def close_issue(repo_name, issue_number):
    """
    指定したIssueをクローズする関数
    """
    issue_data = {
        "state": "closed"
    }

    issue_url = f"{GITHUB_API_URL}/repos/{USERNAME}/{repo_name}/issues/{issue_number}"
    response = requests.patch(issue_url, json=issue_data, headers=headers)

    if response.status_code == 200:
        print(f"Issue #{issue_number} はクローズされました。")
    else:
        print(f"Issueのクローズに失敗しました: {response.json()}")

# 実行例
if __name__ == "__main__":
    repo_name = "auto-created-repo"  # 作成するリポジトリ名
    issue_title = "新しいタスク"
    issue_body = "このタスクは自動で作成されました。"

    get_issues(repo_name)

    '''# 1. 新しいリポジトリを作成
    if create_repository(repo_name):
        # 2. Issueを作成
        create_issue(repo_name, issue_title, issue_body)
        
        # 3. Issue一覧を取得
        get_issues(repo_name)
        
        # 4. Issue #1をクローズ
        close_issue(repo_name, 1)'''

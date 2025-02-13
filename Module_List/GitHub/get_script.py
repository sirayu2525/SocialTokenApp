import requests

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

# 例: GitHubのraw URLを指定
github_raw_url = "https://raw.githubusercontent.com/sirayu2525/SocialTokenApp/refs/heads/evaluation_code/Open_AI/GPT1.py"
source_code = fetch_github_code(github_raw_url)
print(source_code)
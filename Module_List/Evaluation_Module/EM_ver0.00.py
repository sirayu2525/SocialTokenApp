import openai
import os
import requests

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
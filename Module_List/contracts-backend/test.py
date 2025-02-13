# なぜかうごかない
import requests
import os
from dotenv import load_dotenv
import json

# ✅ プロキシを環境変数から削除（実行時のみ）
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

load_dotenv(override=True)
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
print(ADMIN_API_KEY)

API_URL = "http://127.0.0.1:8000/mint_tokens"
headers = {
    "api-key": ADMIN_API_KEY,
    "Content-Type": "application/json"
}

data = {
    "wallet_id": "0xd525f542c3F2d16D12dA68578bd69d068A854BD0",
    "token": 10.0  # 🔹 10 MOP を発行
}
json_data = json.dumps(data)


print("🔹 APIリクエストを送信中...")
response = requests.post(API_URL, headers=headers, data=json_data, proxies=None, verify=False) 

print("🔹 レスポンス受信")
print(response.status_code)
print(response.text)
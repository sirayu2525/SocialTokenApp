import asyncio
import json
import os
from dotenv import load_dotenv
from websockets import connect

# ✅ 環境変数をロード
load_dotenv()

# ✅ .env からAPIキーを取得
INFURA_API_KEY = os.getenv("INFURA_API_KEY")
infura_ws_url = f"wss://sepolia.infura.io/ws/v3/{INFURA_API_KEY}"

async def get_event():
    async with connect(infura_ws_url) as ws:
        subscribe_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            "params": ["newPendingTransactions"]
        }
        await ws.send(json.dumps(subscribe_request))
        
        subscription_response = await ws.recv()
        print(f"📩 購読応答: {subscription_response}")

        while True:
            message = await ws.recv()
            event = json.loads(message)
            print(f"🚀 ペンディングトランザクション: {event}")

# ✅ asyncioで実行
asyncio.run(get_event())

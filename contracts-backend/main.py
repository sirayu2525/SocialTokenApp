from web3 import Web3
import os
#from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import time

#load_dotenv()

INFURA_URL = os.getenv("INFURA_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
print("INFURA_URL:", INFURA_URL)
print("PRIVATE_KEY:", PRIVATE_KEY)
print("CONTRACT_ADDRESS:", CONTRACT_ADDRESS)
print("ADMIN_API_KEY:", ADMIN_API_KEY)


web3 = Web3(Web3.HTTPProvider(INFURA_URL))

contract_abi = [
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "symbol",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "initialSupply",
          "type": "uint256"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "spender",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "allowance",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "needed",
          "type": "uint256"
        }
      ],
      "name": "ERC20InsufficientAllowance",
      "type": "error"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "sender",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "balance",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "needed",
          "type": "uint256"
        }
      ],
      "name": "ERC20InsufficientBalance",
      "type": "error"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "approver",
          "type": "address"
        }
      ],
      "name": "ERC20InvalidApprover",
      "type": "error"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "receiver",
          "type": "address"
        }
      ],
      "name": "ERC20InvalidReceiver",
      "type": "error"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "sender",
          "type": "address"
        }
      ],
      "name": "ERC20InvalidSender",
      "type": "error"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "spender",
          "type": "address"
        }
      ],
      "name": "ERC20InvalidSpender",
      "type": "error"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "owner",
          "type": "address"
        }
      ],
      "name": "OwnableInvalidOwner",
      "type": "error"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "account",
          "type": "address"
        }
      ],
      "name": "OwnableUnauthorizedAccount",
      "type": "error"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "indexed": True,
          "internalType": "address",
          "name": "spender",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "Approval",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "previousOwner",
          "type": "address"
        },
        {
          "indexed": True,
          "internalType": "address",
          "name": "newOwner",
          "type": "address"
        }
      ],
      "name": "OwnershipTransferred",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "from",
          "type": "address"
        },
        {
          "indexed": True,
          "internalType": "address",
          "name": "to",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "Transfer",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "spender",
          "type": "address"
        }
      ],
      "name": "allowance",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "spender",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "approve",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "account",
          "type": "address"
        }
      ],
      "name": "balanceOf",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "decimals",
      "outputs": [
        {
          "internalType": "uint8",
          "name": "",
          "type": "uint8"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "recipient",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "amount",
          "type": "uint256"
        }
      ],
      "name": "mint",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "name",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "renounceOwnership",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "symbol",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "totalSupply",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "to",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "transfer",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "from",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "to",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "transferFrom",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "newOwner",
          "type": "address"
        }
      ],
      "name": "transferOwnership",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "recipient",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "amount",
          "type": "uint256"
        }
      ],
      "name": "transferTokens",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
]

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
def mint_tokens(wallet_id, amount):
    """ `mint()` を実行し、トークンを発行する """
    try:
        account = web3.eth.account.from_key(PRIVATE_KEY)
        nonce = web3.eth.get_transaction_count(account.address, "pending")
        gas_price = web3.eth.gas_price

        print(f"🔹 {wallet_id} に {web3.from_wei(amount, 'ether')} MOP を発行中...")
        print(f"⛽ 現在のガス価格: {web3.from_wei(gas_price, 'gwei')} Gwei")

        txn = contract.functions.mint(wallet_id, amount).build_transaction({
            "from": account.address,
            "gas": 100000,
            "gasPrice": gas_price * 2,
            "nonce": nonce
        })

        signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

        return web3.to_hex(tx_hash)

    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return None


def check_transaction_status_infura(tx_hash):
    """ Infura API を使ってトランザクションの状態をチェックする """
    try:
        response = web3.eth.get_transaction_receipt(tx_hash)
        if response is not None and response.get("status") == 1:
            return "confirmed"  # ✅ トランザクションが承認された
        return "pending"  # ✅ まだ承認されていない
    except Exception:
        return "unknown"  # ✅ 何らかのエラーが発生


def wait_for_mint(tx_hash, timeout=100):
    """ `mint()` のトランザクションがブロックに承認されるのを待機 """
    print("⏳ トークン発行がブロックに承認されるのを待機中...")
    for _ in range(timeout):
        time.sleep(1)
        status = check_transaction_status_infura(tx_hash)
        if status == "confirmed":
            print("✅ トークン発行がブロックに承認されました！")
            return True
    print("❌ トランザクションが確認できませんでした。")
    return False


# ✅ FastAPI のエンドポイント
app = FastAPI()

@app.get("/wallet_balance/{wallet_id}")
def wallet_balance(wallet_id: str):
    """
    🔹 指定したウォレットのトークン残高を取得する API
    """
    if not wallet_id or len(wallet_id) != 42:
        raise HTTPException(status_code=400, detail="Invalid wallet address")

    try:
        balance_wei = contract.functions.balanceOf(wallet_id).call()
        balance = web3.from_wei(balance_wei, "ether")
        return {"status": "Success", "wallet_id": wallet_id, "wallet_balance": balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 リクエストボディのデータモデル
class MintRequest(BaseModel):
    wallet_id: str
    token: float

@app.post("/mint_tokens")
def mint_tokens_api(request: MintRequest, api_key: str = Header(None)):
    """
    🔹 ウォレットにトークンを発行する API
    """
    if api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if not request.wallet_id or len(request.wallet_id) != 42:
        raise HTTPException(status_code=400, detail="Invalid wallet address")

    amount_wei = web3.to_wei(request.token, "ether")

    # ✅ 発行前のトークン残高を取得
    initial_balance_wei = contract.functions.balanceOf(request.wallet_id).call()

    tx_hash = mint_tokens(request.wallet_id, amount_wei)

    if not tx_hash:
        raise HTTPException(status_code=500, detail="Token minting failed. Transaction hash is None.")

    success = wait_for_mint(tx_hash, timeout=100)

    # ✅ 承認された場合のみ `new_balance` を取得
    if success:
        new_balance_wei = contract.functions.balanceOf(request.wallet_id).call()
    else:
        new_balance_wei = initial_balance_wei  # ✅ 失敗した場合は元の残高を返す

    # ✅ 実際に追加されたトークン量を計算
    minted_amount = new_balance_wei - initial_balance_wei

    return {
        "status": "Success",
        "tx_hash": tx_hash,
        "minted_amount": web3.from_wei(minted_amount, "ether"),  # ✅ 追加されたトークン量
        "new_balance": web3.from_wei(new_balance_wei, "ether")   # ✅ 現在のトークン残高
    }

# ✅ テスト用
if __name__ == "__main__":
    wallet_id = "0xd525f542c3F2d16D12dA68578bd69d068A854BD0"
    token_amount = 10  # 🔹 10 MOP
    amount_wei = web3.to_wei(token_amount, "ether")

    try:
        print(f"🔹 {wallet_id} に {token_amount} MOP を発行中...")
        tx_hash = mint_tokens(wallet_id, amount_wei)

        if tx_hash:
            print(f"✅ トークン発行トランザクション: {tx_hash}")

            # ✅ 10秒間トランザクションの確認
            success = wait_for_mint(tx_hash, timeout=100)

            if success:
                new_balance = contract.functions.balanceOf(wallet_id).call()
                print(f"💰 新しいトークン残高: {web3.from_wei(new_balance, 'ether')} MOP")
            else:
                print("❌ トランザクションの確認ができなかったため、仮の残高を表示")

        else:
            print("❌ トークン発行に失敗しました")

    except Exception as e:
        print(f"❌ エラー: {str(e)}")

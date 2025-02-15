import requests
import urllib3

# 自己署名証明書使用時の警告を抑制する
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TokenApiClient:
    """
    APIクライアントクラス
    - /wallet_balance/{wallet_id} エンドポイントによりウォレット残高を取得
    - /mint_tokens エンドポイントによりトークン発行をリクエスト
    """

    def __init__(self, base_url: str, admin_api_key: str = None, timeout: int = 10):
        """
        Args:
            base_url (str): APIサーバーのベースURL（例: "https://localhost:8000"）
            admin_api_key (str): /mint_tokens エンドポイント用の管理者APIキー
            timeout (int): リクエストタイムアウト（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.admin_api_key = admin_api_key
        self.timeout = timeout

    def get_wallet_balance(self, wallet_id: str) -> dict:
        """
        指定したウォレットアドレスのトークン残高を取得する

        Args:
            wallet_id (str): ウォレットアドレス (例: "0x1234...")

        Returns:
            dict: サーバーからのレスポンス（例: {"status": "Success", "wallet_id": "...", "wallet_balance": ...}）
        
        Raises:
            Exception: エラー発生時に詳細情報を含む例外
        """
        url = f"{self.base_url}/wallet_balance/{wallet_id}"
        try:
            response = requests.get(url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"ウォレット残高の取得に失敗しました: {str(e)}")

    def mint_tokens(self, wallet_id: str, token: float) -> dict:
        """
        指定したウォレットにトークンを発行するリクエストを送信する

        Args:
            wallet_id (str): トークン発行先のウォレットアドレス
            token (float): 発行するトークン量（例: 10 なら10 MOP）

        Returns:
            dict: サーバーからのレスポンス（例: {
                "status": "Success",
                "tx_hash": "0x...",
                "minted_amount": ...,
                "new_balance": ...
            })

        Raises:
            Exception: APIエラー時に例外を送出
        """
        url = f"{self.base_url}/mint_tokens"
        headers = {}
        if self.admin_api_key:
            headers["api-key"] = self.admin_api_key

        payload = {
            "wallet_id": wallet_id,
            "token": token
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout, verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"トークン発行のリクエストに失敗しました: {str(e)}")

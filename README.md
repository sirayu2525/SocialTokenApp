# SocialTokenApp(memo)

npm install
npx hardhat init(いらない？)

## ローカルノード
npx hardhat node 
npx hardhat ignition deploy ignition/modules/SocialTokenModule.js --network localhost

## テストネット
hardhat.config.jsでsepoliaを確認
npx hardhat ignition deploy ignition/modules/SocialTokenModule.js --network sepolia
コントラクトアドレスをメモ

## backend
テスト
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
python3 test.py
```
学校の変なプロキシのせいで全然うまくいかなかった（怒）
--verboseで詳しく調べたらプロキシのせいでした。
--noproxy 127.0.0.1をつけたらうまくいった。



#!/bin/sh

# # Python のスクリプトを呼び出して証明書を自動生成
# python -c "from main import generate_self_signed_cert; generate_self_signed_cert('cert.pem', 'key.pem', 'localhost')"

# uvicorn を HTTPS オプション付きで起動
exec uvicorn main:app --host 0.0.0.0 --port 80

FROM python:3.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なシステムパッケージのインストール（PostgreSQL用ヘッダなど）
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# 依存ライブラリをコピー＆インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# entrypoint.sh をコピーして実行権限を付与
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# コンテナが公開するポートを指定（HTTP:80, HTTPS:443 両方公開可能）
EXPOSE 80 443

# エントリーポイントスクリプトで起動
CMD ["./entrypoint.sh"]

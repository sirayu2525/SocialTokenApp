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

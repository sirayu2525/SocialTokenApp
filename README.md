# SocialTokenApp

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

## デプロイ

以下は、GitHubによる自動デプロイ、DockerでFastAPIをSakura VPSにデプロイし、Nginxをリバースプロキシとして追加する手順です。

### 1. プロジェクト構成

```
SocialTokenApp/
    ├── contracts-backend/
    │   ├── main.py
    │   ├── requirements.txt
    │   ├── Dockerfile
    │   └── .env
    ├── docker-compose.yml
    ├── nginx/
    │   └── nginx.conf
    └── .github/
        └── workflows/
            └── deploy.yml
```

### 2. Dockerfile

```Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### 3. docker-compose.yml

```yaml
services:
  fastapi:
    build: ./contracts-backend
    container_name: fastapi_app
    ports:
      - "8000:8000"
    env_file:
      - ./contracts-backend/.env
    restart: always

  nginx:
    image: nginx:latest
    container_name: nginx_proxy
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    env_file:
      - ./contracts-backend/.env
    depends_on:
      - fastapi
```

### 4. nginx/nginx.conf

```nginx
worker_processes auto;
events {
    worker_connections 1024;
    multi_accept on;
}
http {
    server {
        listen 80;
        server_name your_domain_or_ip;

        location / {
            proxy_pass http://fastapi:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

### 5. GitHub Actions 設定

`.github/workflows/deploy.yml`

```yaml
name: Deploy to Sakura VPS

on:
  push:
    branches:
      - tyyti-dev

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Create .env file
      run: |
        echo "INFURA_URL=${{ secrets.INFURA_URL }}" >> ./contracts-backend/.env
        echo "PRIVATE_KEY=${{ secrets.PRIVATE_KEY }}" >> ./contracts-backend/.env
        echo "CONTRACT_ADDRESS=${{ secrets.CONTRACT_ADDRESS }}" >> ./contracts-backend/.env
        echo "ADMIN_API_KEY=${{ secrets.ADMIN_API_KEY }}" >> ./contracts-backend/.env
        echo "API_SERVER_IP=${{ secrets.API_SERVER_IP }}" >> ./contracts-backend/.env

    - name: Deploy with SSH
      uses: appleboy/ssh-action@v0.1.6
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SERVER_SSH_KEY }}
        script: |
          cd ~/SocialTokenApp
          git pull origin tyyti-dev
          docker compose down
          docker compose up -d --build
```

### 6. Sakura VPSでの初期設定

```bash
ssh user@your_server_ip
sudo apt update && sudo apt install docker docker-compose nginx -y
# # ディレクトリ作成
# mkdir -p ~/SocialTokenApp && cd ~/SocialTokenApp
git clone git@github.com:your_user/your_repo.git .
docker-compose up -d
```

### 7. GitHub Secrets

GitHubリポジトリの「Settings」→「Secrets」→「New repository secret」で以下を追加：

- `SERVER_HOST`: VPSのIPアドレス
- `SERVER_USER`: VPSのユーザー名
- `SERVER_SSH_KEY`: ローカルで`~/.ssh/id_rsa`の内容

### 8. 動作確認

ブラウザで `http://your_domain_or_ip/` にアクセスしてFastAPIアプリが表示されることを確認します。

### 9. トラブルシューティング

- Nginxが起動しているか確認: `docker logs nginx_proxy`
- FastAPIが起動しているか確認: `docker logs fastapi_app`
- Docker全体の状態確認: `docker-compose ps`

この構成で、GitHubへのプッシュをトリガーに自動でSakura VPSにFastAPIアプリがデプロイされ、Nginxがリバースプロキシとして機能します。

どうして


SocialTokenApp/
├── docker-compose.yml         ← 統合用 Docker Compose
├── nginx/
│   └── nginx.conf             ← Nginx設定
├── contracts-backend/
│   ├── Dockerfile             ← FastAPI用 Dockerfile
│   ├── main.py                ← FastAPIアプリケーション
│   └── .env                   ← 環境変数ファイル
└── db/
    └── init.sql               ← データベース初期化スクリプト


services:
  db:
    image: postgres:14
    container_name: postgres_db
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydatabase
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      # - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app_network
    restart: always

  db_api:
    build: ./DB_server
    container_name: db_api
    ports:
      - "8001:80"  # ← ホスト側は8001番にすることでFastAPIの8000番と競合回避
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://myuser:mypassword@db:5432/mydatabase
    networks:
      - app_network
    restart: always
    
  fastapi:
    build: ./contracts-backend
    container_name: fastapi_app
    env_file:
      - ./contracts-backend/.env
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://myuser:mypassword@db:5432/mydatabase
    depends_on:
      - db
    networks:
      - app_network
    restart: always

  nginx:
    image: nginx:latest
    container_name: nginx_proxy
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - fastapi
      - db_api
    networks:
      - app_network
    restart: always

volumes:
  postgres_data:

networks:
  app_network:
    driver: bridge

worker_processes auto;

events {
    worker_connections 1024;
}

http {
    upstream fastapi {
        server fastapi:8000;
    }

    upstream db_api {
        server db_api:80; 
    }

    server {
        listen 80;

        # ✅ ユーザー用API (FastAPI)
        location /api/ {
            proxy_pass http://fastapi;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # ✅ DB管理用API (DB_server)
        location /db/ {
            proxy_pass http://db_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # ✅ エラーページ設定
        error_page 404 /404.html;
        location = /404.html {
            internal;
        }

        # ✅ バッファ設定（FastAPI応答最適化）
        client_max_body_size 10M;
        proxy_read_timeout 120;
        proxy_connect_timeout 120;
        proxy_send_timeout 120;
    }
}

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

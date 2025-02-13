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
version: '3.7'
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
    environment:
      - API_SERVER_IP=${API_SERVER_IP}
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
    resolver 127.0.0.11;

    server {
        listen 80;
        server_name your_domain_or_ip;

        location / {
            proxy_pass http://$API_SERVER_IP:8000;
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
        echo "INFURA_URL=${{ secrets.INFURA_URL }}" >> .contracts-backend/.env
        echo "PRIVATE_KEY=${{ secrets.PRIVATE_KEY }}" >> .contracts-backend/.env
        echo "CONTRACT_ADDRESS=${{ secrets.CONTRACT_ADDRESS }}" >> .contracts-backend/.env
        echo "ADMIN_API_KEY=${{ secrets.ADMIN_API_KEY }}" >> .contracts-backend/.env
        echo "API_SERVER_IP=${{ secrets.API_SERVER_IP }}" >> .contracts-backend/.env

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


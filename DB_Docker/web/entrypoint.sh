#!/bin/sh

# Python のスクリプトを呼び出して証明書を自動生成
#python -c "from main import generate_self_signed_cert; generate_self_signed_cert('cert.pem', 'key.pem', 'localhost')"

# uvicorn を HTTPS オプション付きで起動
#exec uvicorn main:app --host 0.0.0.0 --port 443 --ssl-keyfile key.pem --ssl-certfile cert.pem

#!/bin/sh

# FastAPI (ユーザー用) を起動
exec uvicorn main:app --host 0.0.0.0 --port 8000

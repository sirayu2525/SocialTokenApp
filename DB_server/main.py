import os
import datetime
from typing import Any, Dict

from fastapi import FastAPI, Depends, HTTPException, Header, Request, Body
from fastapi.routing import APIRoute
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, text
from database import SessionLocal, engine, Base

from fastapi import Query

import urllib

import json

from database import engine
from models import DataRecord

# テーブルを作成（まだ作成していない場合）
Base.metadata.create_all(bind=engine)

# ----- 自己署名証明書の自動生成処理 -----
#from cryptography import x509
#from cryptography.x509.oid import NameOID
#from cryptography.hazmat.primitives import hashes, serialization
#from cryptography.hazmat.primitives.asymmetric import rsa

'''def generate_self_signed_cert(cert_file: str, key_file: str, hostname: str = "localhost"):
    if os.path.exists(cert_file) and os.path.exists(key_file):
        return

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow() - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(hostname)]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    with open(key_file, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

# モジュール読み込み時に証明書を自動生成
generate_self_signed_cert("cert.pem", "key.pem", hostname="localhost")'''

# ----- グローバル API キー認証（docs 関連は除外） -----
API_KEY = "mysecretkey"

class APIKeyRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request):
            # ドキュメント関連は認証スキップ
            if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
                return await original_route_handler(request)
            api_key = request.headers.get("X-API-Key")
            if api_key != API_KEY:
                raise HTTPException(status_code=403, detail="Invalid API Key")
            return await original_route_handler(request)
        return custom_route_handler

app = FastAPI(
    title="FastAPI DB Operations API Server",
    route_class=APIKeyRoute
)

# ----- DB セッション取得用依存関数 -----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- DB 操作用クラス -----
class DBManager:
    def __init__(self, db: Session):
        self.db = db

    def create_tables(self, table_name: str = None):
        if table_name:
            if table_name in Base.metadata.tables:
                Base.metadata.tables[table_name].create(bind=engine, checkfirst=True)
            else:
                raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in metadata")
        else:
            Base.metadata.create_all(bind=engine)

    def table_exists(self, table_name: str) -> bool:
        with engine.connect() as connection:
            return engine.dialect.has_table(connection, table_name)

    def add_data(self, table_name: str, data: Dict[str, Any]) -> dict:
        """
        任意のカラムと値の組み合わせでレコードを挿入します。
        なお、data 内のキーがテーブル定義に存在するかを検証します。
        """
        table = Base.metadata.tables.get(table_name)
        if table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        # data のキーがテーブルに存在するかチェック
        for col in data.keys():
            if col not in table.c:
                raise HTTPException(status_code=400, detail=f"Column '{col}' not found in table '{table_name}'")
        stmt = insert(table).values(**data)
        result = self.db.execute(stmt)
        self.db.commit()
        # primary key を使って挿入したレコードを取得（単一の PK を想定）
        pk_columns = list(table.primary_key.columns)
        if pk_columns:
            pk_col = pk_columns[0]
            inserted_pk = result.inserted_primary_key[0] if result.inserted_primary_key else None
            if inserted_pk is not None:
                query = select(table).where(pk_col == inserted_pk)
                row = self.db.execute(query).fetchone()
                return dict(row._mapping) if row else {}
        return {}

    def get_data_by_field(self, table_name: str, column: str, value: Any) -> dict:
        table = Base.metadata.tables.get(table_name)
        if table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        if column not in table.c:
            raise HTTPException(status_code=400, detail="Invalid column name")
        query = select(table).where(table.c[column] == value)
        row = self.db.execute(query).fetchone()
        return dict(row._mapping) if row else None

    def update_columns(self, table_name: str, column: str, search_value: Any, updates: Dict[str, Any]) -> dict:
        """
        指定した条件に合致する行の、複数のカラムの値を一括で更新する。

        :param table_name: 更新するテーブル名
        :param column: 検索対象のカラム名
        :param search_value: 検索する値
        :param updates: 更新するカラム名と新しい値の辞書（例: {"col1": "new_value1", "col2": "new_value2"}）
        :return: 更新後のデータ（辞書形式）
        """
        table = Base.metadata.tables.get(table_name)
        if table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

        # 検索条件のカラムがテーブルに存在するかチェック
        if column not in table.c:
            raise HTTPException(status_code=400, detail=f"Invalid search column: '{column}'")

        # 更新対象のカラムが全てテーブルに存在するかチェック
        for target_column in updates.keys():
            if target_column not in table.c:
                raise HTTPException(status_code=400, detail=f"Invalid target column: '{target_column}'")

        # 更新前のレコードを取得
        query = select(table).where(table.c[column] == search_value)
        row = self.db.execute(query).fetchone()
        if not row:
            return None

        # 更新処理
        upd = update(table).where(table.c[column] == search_value).values(**updates)
        self.db.execute(upd)
        self.db.commit()

        # 更新後のデータを取得して返す
        row = self.db.execute(query).fetchone()
        return dict(row._mapping) if row else None


    def add_column(self, table_name: str, column_name: str, column_type: str):
        """
        指定したテーブルに新しい列を追加します。
        column_type には "VARCHAR(255)" や "INTEGER" など、データベースの型定義を文字列で指定します。
        """
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};"
        self.db.execute(text(sql))
        self.db.commit()

# ----- エンドポイント定義 -----
@app.post("/create_tables")
def create_tables(table_name: str = None, db: Session = Depends(get_db)):
    manager = DBManager(db)
    manager.create_tables(table_name)
    if table_name:
        return {"message": f"Table '{table_name}' created successfully"}
    else:
        return {"message": "All tables created successfully"}

@app.get("/table_exists/{table_name}")
def check_table_exists(table_name: str, db: Session = Depends(get_db)):
    manager = DBManager(db)
    exists = manager.table_exists(table_name)
    return {"table": table_name, "exists": exists}

@app.post("/data")
def add_data(table_name: str, data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """
    任意のカラムと値の組み合わせでレコードを追加するエンドポイント
    リクエストボディは JSON 形式で、例:
    {
      "data": {
         "col1": "value1",
         "col2": 123,
         "col3": "value3"
      }
    }
    ※ 今回は直接 dict を受け取るため、ラップするキーは不要です。
    """
    manager = DBManager(db)
    record = manager.add_data(table_name, data)
    return record

@app.get("/data/search")
def get_data_by_field(table_name: str, column: str, value: Any, db: Session = Depends(get_db)):
    manager = DBManager(db)
    record = manager.get_data_by_field(table_name, column, value)
    #if record is None:
    #    raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.get("/data/update_columns")
def update_columns(
    table_name: str,
    column: str,
    search_value: Any,
    updates: str = Query(...),  # updatesをJSON文字列として受け取る
    db: Session = Depends(get_db)
):
    """
    特定の条件に一致するレコードの複数のカラムを一括更新するエンドポイント（GETリクエスト）

    クエリ例:
    /data/update_columns?table_name=your_table&column=col1&search_value=value1&updates={"col2": "new_value1", "col3": "new_value2"}
    """
    try:
        updates_decoded = urllib.parse.unquote(updates)  # URLデコード
        updates_dict = json.loads(updates_decoded)  # JSON文字列を辞書に変換
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for 'updates'")

    manager = DBManager(db)
    record = manager.update_columns(table_name, column, search_value, updates_dict)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record



@app.post("/add_column")
def add_column_endpoint(table_name: str, column_name: str, column_type: str, db: Session = Depends(get_db)):
    """
    指定したテーブルに新しい列を追加するエンドポイント
    """
    manager = DBManager(db)
    try:
        manager.add_column(table_name, column_name, column_type)
        return {"message": f"Column '{column_name}' of type '{column_type}' added to table '{table_name}' successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
import sqlite3
from typing import List, Tuple, Optional

class DatabaseManager:
    def __init__(self, db_name: str = "database.db"):
        """SQLiteデータベースを管理するクラス"""
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def table_exists(self, table_name: str) -> bool:
        """指定したテーブルがデータベースに存在するか判定する"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        self.cursor.execute(query, (table_name,))
        return self.cursor.fetchone() is not None

    def create_table(self, table_name: str, columns: str):
        """テーブルを作成する"""
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert(self, table_name: str, columns: Tuple[str], values: Tuple):
        """データを挿入する"""
        placeholders = ', '.join(['?'] * len(values))
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def fetch_all(self, table_name: str) -> List[Tuple]:
        """すべてのレコードを取得する"""
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_one(self, table_name: str, condition: str, params: Tuple) -> Optional[Tuple]:
        """条件に一致する1件のレコードを取得する"""
        query = f"SELECT * FROM {table_name} WHERE {condition}"
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def update(self, table_name: str, updates: str, condition: str, params: Tuple):
        """レコードを更新する"""
        query = f"UPDATE {table_name} SET {updates} WHERE {condition}"
        self.cursor.execute(query, params)
        self.conn.commit()

    def delete(self, table_name: str, condition: str, params: Tuple):
        """レコードを削除する"""
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.cursor.execute(query, params)
        self.conn.commit()

    def exists(self, table_name: str, condition: str, params: Tuple) -> bool:
        """
        条件に合致するデータが存在するか確認する
        :param table_name: テーブル名
        :param condition: WHERE 句の条件 (例: "name = ?")
        :param params: 条件の値 (例: ("Alice",))
        :return: 存在すれば True、なければ False
        """
        query = f"SELECT 1 FROM {table_name} WHERE {condition} LIMIT 1"
        self.cursor.execute(query, params)
        return self.cursor.fetchone() is not None

    def upsert(self, table_name: str, columns: Tuple[str], values: Tuple, unique_column: str):
        """
        既存のデータを上書き編集する（存在しない場合は挿入）
        :param table_name: テーブル名
        :param columns: 挿入/更新する列名 (例: ("name", "age"))
        :param values: 挿入/更新する値 (例: ("Alice", 30))
        :param unique_column: 一意な識別列 (例: "name")
        """
        condition = f"{unique_column} = ?"
        unique_value = (values[columns.index(unique_column)],)

        if self.exists(table_name, condition, unique_value):
            # 既存データがある場合は更新
            updates = ', '.join([f"{col} = ?" for col in columns])
            query = f"UPDATE {table_name} SET {updates} WHERE {condition}"
            self.cursor.execute(query, values + unique_value)
        else:
            # 既存データがない場合は挿入
            self.insert(table_name, columns, values)

        self.conn.commit()

    def close(self):
        """データベース接続を閉じる"""
        self.conn.close()

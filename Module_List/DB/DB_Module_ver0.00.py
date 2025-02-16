import sqlite3
from typing import List, Tuple, Optional

class DatabaseManager:
    def __init__(self, db_name: str = "database.db"):
        """SQLiteデータベースを管理するクラス"""
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def table_exists(self, table_name: str) -> bool:
        """
        指定したテーブルがデータベースに存在するか判定する
        :param table_name: 確認するテーブル名
        :return: 存在すれば True、存在しなければ False
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        self.cursor.execute(query, (table_name,))
        return self.cursor.fetchone() is not None

    def create_table(self, table_name: str, columns: str):
        """テーブルを作成する"""
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {columns}
        )"""
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

    def close(self):
        """データベース接続を閉じる"""
        self.conn.close()

# 使用例
'''
db = DatabaseManager("example.db")
db.create_table("users", "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, age INTEGER")
db.insert("users", ("name", "age"), ("Alice", 25))
print(db.fetch_all("users"))  # [(1, 'Alice', 25)]
db.update("users", "age = ?", "name = ?", (26, "Alice"))
print(db.fetch_one("users", "name = ?", ("Alice",)))  # (1, 'Alice', 26)
db.delete("users", "name = ?", ("Alice",))
db.close()
'''
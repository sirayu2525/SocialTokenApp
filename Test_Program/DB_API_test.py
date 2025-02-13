import requests
import urllib3

# 自己署名証明書の警告を無効化（開発環境のみ）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DatabaseClient:
    def __init__(self, base_url, api_key):
        """
        :param base_url: APIサーバーのURL (例: "https://localhost")
        :param api_key: アクセス用 API キー
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {"X-API-Key": api_key}

    def create_tables(self, table_name=None):
        params = {}
        if table_name:
            params['table_name'] = table_name
        response = requests.post(
            f"{self.base_url}/create_tables",
            params=params,
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()

    def table_exists(self, table_name):
        response = requests.get(
            f"{self.base_url}/table_exists/{table_name}",
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()

    def add_data(self, table_name, key, value):
        params = {'table_name': table_name, 'key': key, 'value': value}
        response = requests.post(
            f"{self.base_url}/data",
            params=params,
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()

    def get_data_by_field(self, table_name, column, value):
        params = {'table_name': table_name, 'column': column, 'value': value}
        response = requests.get(
            f"{self.base_url}/data/search",
            params=params,
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()

    def update_column(self, table_name, column, search_value, target_column, new_value):
        """
        指定した条件に合致する行の、特定のカラムの値を新しい値に置き換える
        :param table_name: 更新するテーブル名
        :param column: 検索対象のカラム名
        :param search_value: 検索する値
        :param target_column: 更新対象のカラム名
        :param new_value: 設定する新しい値
        :return: 更新後のデータ（辞書形式）
        """
        params = {
            'table_name': table_name,
            'column': column,
            'search_value': search_value,
            'target_column': target_column,
            'new_value': new_value
        }
        response = requests.put(
            f"{self.base_url}/data/update_column",
            params=params,
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    base_url = "https://localhost:50403"  # 必要に応じてホスト名/ポートを調整
    api_key = "mysecretkey"
    client = DatabaseClient(base_url, api_key)

    # 例として、"data_records" というテーブル名を指定（models.py の __tablename__ と一致させる）
    table_name = "new_records"

    try:
        # テーブル作成
        print("Creating table:")
        print(client.create_tables(table_name))

        # テーブル存在確認
        print("\nChecking table existence:")
        print(client.table_exists(table_name))

        # データの追加
        print("\nAdding data:")
        added = client.add_data(table_name, "example_key", "example_value")
        print(added)

        # データの検索
        print("\nSearching data by field:")
        found = client.get_data_by_field(table_name, "key", "example_key")
        print(found)

        # 特定のカラムを更新
        print("\nUpdating specific column:")
        updated = client.update_column(table_name, "key", "example_key", "value", "new_updated_value")
        print(updated)

    except requests.HTTPError as http_err:
        print("HTTP error occurred:", http_err)
    except Exception as err:
        print("Unexpected error occurred:", err)

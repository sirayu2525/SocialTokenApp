import time
from smartcard.System import readers
from smartcard.util import toHexString

# カードリーダーのリストを取得
r = readers()
if len(r) == 0:
    print("カードリーダーが見つかりません")
    exit()

# 使用するカードリーダーを選択
reader = r[0]
print(f"使用するカードリーダー: {reader}")

# リーダーに接続
connection = reader.createConnection()
connection.connect()

# ビープ音を鳴らすコマンド（ACR122U用）
command = [0xFF, 0x00, 0x52, 0x00, 0x01]  # ビープ音を鳴らすコマンド

# 音を繰り返し鳴らす（間隔を調整）
for _ in range(3):  # 3回音を鳴らす
    response, sw1, sw2 = connection.transmit(command)
    print(f"応答: {toHexString(response)} SW1: {sw1} SW2: {sw2}")
    time.sleep(0.5)  # 0.5秒の間隔を空ける

# ここで音が繰り返され、音の長さを調整できます

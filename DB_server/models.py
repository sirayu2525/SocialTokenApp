# models.py
from sqlalchemy import Column, Integer, String, JSON
from database import Base

class DataRecord(Base):
    __tablename__ = "data_records"

    id = Column(Integer, primary_key=True, index=True)  # 自動インクリメントの ID
    discord_name = Column(String(100), default='')  # Discordアカウント名
    github_username = Column(String(100), default='')  # GitHubユーザー名
    balance = Column(Integer, default=0)  # 残高（日本円）
    wallet_id = Column(String(255), unique=True, default='')  # ウォレットID（文字列）
    tx_hashes = Column(JSON, default=[])  # 取引履歴（リスト型）
    card_IDm = Column(String(100), default='')

'''class DataRecord(Base):
    __tablename__ = "data_records"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, index=True)
    value = Column(String)
'''
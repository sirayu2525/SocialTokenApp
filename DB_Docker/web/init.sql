-- 初期テーブル作成
CREATE TABLE users (
    id SERIAL PRIMARY KEY,                          -- ユーザーID（自動インクリメント）
    discord_name VARCHAR(100) NOT NULL,            -- Discordアカウント名
    github_username VARCHAR(100) NOT NULL,         -- GitHubユーザー名
    balance INTEGER DEFAULT 0,                     -- 残高（日本円）
    wallet_id NOT NULL UNIQUE,                -- ウォレットID
    tx_hashes JSONB DEFAULT '[]'                   -- 取引のtx_hash（JSONBリスト）
);

-- 初期データ挿入
INSERT INTO users (discord_name, github_username, balance, wallet_id, tx_hashes)
VALUES
('Alice#1234', 'alice-github', 5000, 'ASD1', '["tx1_hash", "tx2_hash"]'),
('Bob#5678', 'bob-github', 10000, 'ASD2', '["tx3_hash"]');

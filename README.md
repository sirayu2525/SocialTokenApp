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
uvicorn mint_tokens:app --reload
python3 test.py
```
学校の変なプロキシのせいで全然うまくいかなかった（怒）
--verboseで詳しく調べたらプロキシのせいでした。
--noproxy 127.0.0.1をつけたらうまくいった。
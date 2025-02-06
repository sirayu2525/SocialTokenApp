# SocialTokenApp

## 環境構築

前提：WSLのUbuntu

### フロントエンド
Node.jsとnpmのインストール
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
source ~/.bashrc
nvm install --lts
node -v  # インストール確認
npm -v   # インストール確認
```
Reactアプリケーションの作成
```bash
npx create-react-app frontend 
npm install react@18 react-dom@18 #依存関係の解消のためReact18にダウングレード
cd frontend
# 必要があれば　npm install web-vitals
npm install ethers
```

### バックエンド

Hardhatの初期化時には「Create a basic sample project」を選択
```bash
mkdir backend
cd backend
npm init -y
npm install --save-dev hardhat
npx hardhat init
```

各種ファイル生成
```bash
touch contracts/SocialToken.sol
mkdir scripts
touch deploy.js
```

ローカルノードデプロイ
```bash
npm install @openzeppelin/contracts
npx hardhat node # ローカルのブロックチェーンネットワークを立ち上げる
# 別のターミナルに移動
npx hardhat run scripts/local_deploy.js --network localhost # ローカルノードにデプロイ
```
ローカルノードのテスト

方法１(Hatdhatのコンソールから)
```bash
npx hardhat console --network localhost # Hardhatコンソールを起動
const [owner, addr1] = await ethers.getSigners();  # テスト用アカウントを取得
const SocialToken = await ethers.getContractFactory("SocialToken");
const socialToken = await SocialToken.attach("ADDRESSを入力");
# オーナーのトークン残高を確認
const balance = await socialToken.balanceOf(owner.address);
console.log(`Owner balance: ${ethers.formatUnits(balance, 18)} STK`);
# addr1 に 100 トークンを送信
await socialToken.transfer(addr1.address, ethers.parseUnits("100", 18));
# addr1 の残高を確認
const addr1Balance = await socialToken.balanceOf(addr1.address);
console.log(`Recipient balance: ${ethers.formatUnits(addr1Balance, 18)} STK`);
```

方法２（自動的にコントラクトとインタラクション）
```bash
touch scripts/interact.js
npx hardhat run scripts/interact.js --network localhost
```
方法３（ユニットテスト作成）
```bash
touch test/SocialToken.js
npx hardhat test
```



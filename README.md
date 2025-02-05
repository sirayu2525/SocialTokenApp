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
npm install react@18 react-dom@18 #依存関係の解消でReact18にダウングレード
cd frontend
npm install ethers
```
const hre = require("hardhat");
const { ethers } = require("hardhat");

async function main() {
  // トークンの名前、シンボル、初期供給量を設定
  const tokenName = "SocialToken";
  const tokenSymbol = "STK";
  const initialSupply = 1000000; // 1,000,000 トークン

  // コントラクトファクトリを取得してデプロイ
  const SocialToken = await hre.ethers.getContractFactory("SocialToken");
  const socialToken = await SocialToken.deploy(tokenName, tokenSymbol, initialSupply);

  // デプロイ完了まで待機
  await socialToken.deployed();

  console.log(`SocialToken deployed to: ${socialToken.address}`);
}   

// エラー処理
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

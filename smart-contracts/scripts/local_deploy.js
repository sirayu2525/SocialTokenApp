const { ethers } = require("hardhat");

async function main() {
  // トークンの名前、シンボル、初期供給量を設定
  const tokenName = "SocialToken";
  const tokenSymbol = "STK";
  const initialSupply = ethers.parseUnits("1000000", 18);  // 18桁の小数を考慮した供給量
  console.log(typeof initialSupply);  // BigInt 型であることを確認

  // コントラクトをデプロイ
  const socialToken = await ethers.deployContract("SocialToken", [tokenName, tokenSymbol, initialSupply]);

  // デプロイ完了まで待機
  await socialToken.waitForDeployment();

  // デプロイ完了後のコントラクトアドレスを表示
  console.log(`SocialToken deployed to: ${socialToken.target}`);
}

// エラー処理
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

module.exports = buildModule("SocialTokenModule", (m) => {
  // パラメータを取得
  const tokenName = m.getParameter("tokenName", "SocialToken");
  const tokenSymbol = m.getParameter("tokenSymbol", "STK");
  const initialSupply = m.getParameter("initialSupply", "1000000");

  // initialSupplyの値を取り出してBigIntに変換
  const supplyValue = initialSupply.defaultValue || "1000000";
  const initialSupplyBigInt = BigInt(supplyValue) * BigInt(10 ** 18);

  // コントラクトのデプロイ
  const socialToken = m.contract("SocialToken", [
    tokenName,
    tokenSymbol,
    initialSupplyBigInt
  ]);

  return { socialToken };
});

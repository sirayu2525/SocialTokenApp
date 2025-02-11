// const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

// module.exports = buildModule("SocialTokenModule", (m) => {
//   // パラメータを取得
//   const tokenName = m.getParameter("tokenName", "SocialToken");
//   const tokenSymbol = m.getParameter("tokenSymbol", "STK");
//   const initialSupply = m.getParameter("initialSupply", "1000");

//   // initialSupplyの値を取り出してBigIntに変換
//   const supplyValue = initialSupply.defaultValue || "1000";
//   const initialSupplyBigInt = BigInt(supplyValue) * BigInt(10 ** 18);

//   // コントラクトのデプロイ
//   const socialToken = m.contract("SocialToken", [
//     tokenName,
//     tokenSymbol,
//     initialSupplyBigInt
//   ]);

//   return { socialToken };
// });

// ↓シンプルにするため、固定値を直接記述するように変更↓

const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

module.exports = buildModule("SocialTokenModule", (m) => {
  // 固定値を直接記述
  const tokenName = "SocialToken";  // トークン名を固定
  const tokenSymbol = "MOP";        // シンボルを固定
  const initialSupplyBigInt = BigInt(1000000) * BigInt(10 ** 18);  // 100万トークン発行

  // コントラクトのデプロイ
  const socialToken = m.contract("SocialToken", [tokenName, tokenSymbol, initialSupplyBigInt]);

  return { socialToken };
});


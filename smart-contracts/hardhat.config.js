require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

// ネットワークを選択（"localhost" または "sepolia"）
const network = "localhost"; // ここを "sepolia" に変えれば Sepolia 用の設定になる

// ネットワーク設定
const networksConfig = {
  localhost: {
    url: "http://127.0.0.1:8545",
  },
  sepolia: {
    url: process.env.SEPOLIA_RPC_URL,
    accounts: [process.env.PRIVATE_KEY].filter(Boolean),
  },
};

// Hardhat の設定
module.exports = {
  solidity: "0.8.28",
  networks: {
    [network]: networksConfig[network],
  },
};

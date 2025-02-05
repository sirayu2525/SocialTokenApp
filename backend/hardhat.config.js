require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.28",
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545", // ローカルノード
    },
    // mumbai: {
    //   url: "https://rpc-mumbai.maticvigil.com", // PolygonのMumbaiテストネット
    //   accounts: ["YOUR_PRIVATE_KEY"]  // テスト用ウォレットの秘密鍵をここに設定
    // }
  }
};

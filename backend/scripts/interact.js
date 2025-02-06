const { ethers } = require("hardhat");

async function main() {
  const contractAddress = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512";
  const [owner, addr1] = await ethers.getSigners();
  
  // コントラクトに接続
  const SocialToken = await ethers.getContractFactory("SocialToken");
  const socialToken = await SocialToken.attach(contractAddress);

  // オーナーの残高確認
  const ownerBalance = await socialToken.balanceOf(owner.address);
  console.log(`Owner balance: ${ethers.formatUnits(ownerBalance, 18)} STK`);

  // 100 STK を addr1 に送信
  const tx = await socialToken.transfer(addr1.address, ethers.parseUnits("100", 18));
  await tx.wait();  // トランザクションの完了を待機

  // addr1 の残高確認
  const addr1Balance = await socialToken.balanceOf(addr1.address);
  console.log(`Recipient balance: ${ethers.formatUnits(addr1Balance, 18)} STK`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

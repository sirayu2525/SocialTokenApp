const { expect } = require("chai");

describe("SocialToken Contract", function () {
  it("Should deploy with correct initial supply", async function () {
    const [owner] = await ethers.getSigners();
    const SocialToken = await ethers.getContractFactory("SocialToken");
    const socialToken = await SocialToken.deploy("SocialToken", "STK", ethers.parseUnits("1000000", 18));
    await socialToken.waitForDeployment();

    const ownerBalance = await socialToken.balanceOf(owner.address);
    expect(await socialToken.totalSupply()).to.equal(ownerBalance);
  });

  it("Should transfer tokens correctly", async function () {
    const [owner, addr1] = await ethers.getSigners();
    const SocialToken = await ethers.getContractFactory("SocialToken");
    const socialToken = await SocialToken.deploy("SocialToken", "STK", ethers.parseUnits("1000000", 18));
    await socialToken.waitForDeployment();

    await socialToken.transfer(addr1.address, ethers.parseUnits("100", 18));
    const addr1Balance = await socialToken.balanceOf(addr1.address);
    expect(addr1Balance).to.equal(ethers.parseUnits("100", 18));
  });
});

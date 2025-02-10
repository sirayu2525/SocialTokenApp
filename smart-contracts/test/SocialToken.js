// 未検証
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SocialToken", function () {
  let owner, addr1, socialToken;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();

    const SocialToken = await ethers.getContractFactory("SocialToken");
    socialToken = await SocialToken.deploy("SocialToken", "MOP", ethers.parseUnits("1000000", 18));
    await socialToken.waitForDeployment();
  });

  it("should mint tokens only by owner", async function () {
    await socialToken.mint(addr1.address, ethers.parseUnits("500", 18));
    expect(await socialToken.balanceOf(addr1.address)).to.equal(ethers.parseUnits("500", 18));
  });

  it("should not allow non-owner to mint", async function () {
    await expect(
      socialToken.connect(addr1).mint(addr1.address, ethers.parseUnits("500", 18))
    ).to.be.revertedWith("Ownable: caller is not the owner");
  });

  it("should allow owner to transfer tokens", async function () {
    await socialToken.transferTokens(addr1.address, ethers.parseUnits("200", 18));
    expect(await socialToken.balanceOf(addr1.address)).to.equal(ethers.parseUnits("200", 18));
  });

  it("should not allow non-owner to use transferTokens", async function () {
    await expect(
      socialToken.connect(addr1).transferTokens(owner.address, ethers.parseUnits("100", 18))
    ).to.be.revertedWith("Ownable: caller is not the owner");
  });
});

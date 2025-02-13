// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SocialToken is ERC20, Ownable {
    constructor(string memory name, string memory symbol, uint256 initialSupply)
        ERC20(name, symbol)
        Ownable(msg.sender)
    {
        require(initialSupply > 0, "Initial supply must be greater than zero");
        _mint(msg.sender, initialSupply);
    }

    // 🔹 管理者（Owner）のみトークンを送信可能
    function transferTokens(address recipient, uint256 amount) public onlyOwner {
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        _transfer(msg.sender, recipient, amount);
    }


    // 🔹 管理者（Owner）のみ追加発行可能
    function mint(address recipient, uint256 amount) public onlyOwner {
        require(amount > 0, "Mint amount must be greater than zero");
        _mint(recipient, amount);
    }
}

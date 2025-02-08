// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SocialToken is ERC20, Ownable {
    constructor() ERC20("SocialToken", "SCT") {
        _mint(msg.sender, 1000 * 10 ** decimals());
    }

    function issueTokens(address recipient, uint256 amount) public onlyOwner {
        _mint(recipient, amount);
    }
}

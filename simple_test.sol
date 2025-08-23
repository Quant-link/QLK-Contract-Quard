pragma solidity ^0.8.0;

contract SimpleTest {
    uint256 public balance;
    
    function unsafeWithdraw() public {
        msg.sender.call{value: balance}("");
        balance = 0; // State change after external call - REENTRANCY!
    }
}

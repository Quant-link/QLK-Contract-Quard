// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableContract {
    mapping(address => uint256) public balances;
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    // Vulnerable to reentrancy
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance");
        
        // External call before state change - VULNERABLE!
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] = 0; // State change after external call
    }
    
    // Missing access control
    function emergencyWithdraw() public {
        // Anyone can call this! Should be onlyOwner
        payable(msg.sender).transfer(address(this).balance);
    }
    
    // Using tx.origin instead of msg.sender
    function adminFunction() public {
        require(tx.origin == owner, "Not owner"); // VULNERABLE!
        // Admin logic here
    }
    
    // Integer overflow potential (if using older Solidity)
    function unsafeAdd(uint256 a, uint256 b) public pure returns (uint256) {
        return a + b; // No overflow protection
    }
    
    // Timestamp dependence
    function timeBasedFunction() public view returns (bool) {
        return block.timestamp % 2 == 0; // Vulnerable to miner manipulation
    }
    
    // Unchecked external call
    function unsafeCall(address target, bytes calldata data) public {
        target.call(data); // Return value not checked
    }
    
    // Gas limit issue
    function processArray(uint256[] memory arr) public {
        for (uint256 i = 0; i < arr.length; i++) {
            // Unbounded loop - can run out of gas
            balances[msg.sender] += arr[i];
        }
    }
    
    receive() external payable {
        balances[msg.sender] += msg.value;
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableBank {
    mapping(address => uint256) public balances;
    address public owner;
    bool private locked;
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    // VULNERABILITY 1: Reentrancy Attack
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // External call before state change - VULNERABLE!
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount; // State change after external call
    }
    
    // VULNERABILITY 2: Access Control Issue
    function emergencyWithdraw() public {
        // Missing onlyOwner modifier - VULNERABLE!
        uint256 contractBalance = address(this).balance;
        payable(msg.sender).transfer(contractBalance);
    }
    
    // VULNERABILITY 3: Integer Overflow (if using older Solidity)
    function deposit() public payable {
        balances[msg.sender] += msg.value; // Could overflow in older versions
    }
    
    // VULNERABILITY 4: Timestamp Dependence
    function timeLimitedWithdraw() public {
        require(block.timestamp % 2 == 0, "Can only withdraw on even timestamps");
        // Miners can manipulate timestamp - VULNERABLE!
        withdraw(balances[msg.sender]);
    }
    
    // VULNERABILITY 5: Unchecked External Call
    function transferTo(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        
        // Unchecked external call - VULNERABLE!
        to.call{value: amount}("");
    }
    
    // VULNERABILITY 6: Gas Limit DoS
    function massTransfer(address[] memory recipients, uint256[] memory amounts) public {
        require(recipients.length == amounts.length, "Array length mismatch");
        
        // No gas limit check - can cause DoS - VULNERABLE!
        for (uint256 i = 0; i < recipients.length; i++) {
            require(balances[msg.sender] >= amounts[i], "Insufficient balance");
            balances[msg.sender] -= amounts[i];
            balances[recipients[i]] += amounts[i];
        }
    }
    
    // VULNERABILITY 7: tx.origin Usage
    function authorizeWithTxOrigin() public {
        require(tx.origin == owner, "Not authorized"); // Should use msg.sender - VULNERABLE!
        // Critical function logic here
    }
    
    // VULNERABILITY 8: Weak Randomness
    function randomNumber() public view returns (uint256) {
        // Predictable randomness - VULNERABLE!
        return uint256(keccak256(abi.encodePacked(block.timestamp, block.difficulty, msg.sender))) % 100;
    }
    
    // VULNERABILITY 9: Uninitialized Storage Pointer
    struct User {
        address addr;
        uint256 balance;
    }
    
    User[] public users;
    
    function addUser() public {
        User memory newUser; // Uninitialized - VULNERABLE!
        newUser.addr = msg.sender;
        users.push(newUser);
    }
    
    // VULNERABILITY 10: Front-running
    function commitReveal(bytes32 commitment) public payable {
        // Simple commit without proper reveal mechanism - VULNERABLE to front-running!
        require(msg.value > 0, "Must send ether");
        // Store commitment logic
    }
    
    // Helper function to get contract balance
    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }
}

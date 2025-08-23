// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title VulnerableContract
 * @dev This contract contains several intentional vulnerabilities for testing ContractQuard
 */
contract VulnerableContract {
    mapping(address => uint256) public balances;
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    // Vulnerability 1: Reentrancy - state change after external call
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance to withdraw");
        
        // External call before state change - VULNERABLE!
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        // State change after external call - reentrancy vulnerability
        balances[msg.sender] = 0;
    }
    
    // Vulnerability 2: Missing access control
    function emergencyWithdraw() public {
        // No access control - anyone can call this!
        payable(msg.sender).transfer(address(this).balance);
    }
    
    // Vulnerability 3: tx.origin for authorization
    function adminFunction() public {
        require(tx.origin == owner, "Not authorized"); // VULNERABLE!
        // Admin functionality here
    }
    
    // Vulnerability 4: Unchecked external call
    function sendEther(address payable recipient, uint256 amount) public {
        require(msg.sender == owner, "Only owner");
        // Unchecked call - return value not checked
        recipient.call{value: amount}("");
    }
    
    // Vulnerability 5: Timestamp dependence
    function timeLimitedFunction() public {
        require(block.timestamp < 1700000000, "Time limit exceeded"); // VULNERABLE!
        // Function logic here
    }
    
    // Vulnerability 6: Weak randomness
    function generateRandomNumber() public view returns (uint256) {
        // Weak randomness using block properties
        return uint256(keccak256(abi.encodePacked(block.timestamp, block.difficulty))) % 100;
    }
    
    // Good practice: Secure withdraw function
    function secureWithdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance to withdraw");
        
        // State change before external call - secure pattern
        balances[msg.sender] = 0;
        
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
    
    // Good practice: Proper access control
    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }
    
    function secureAdminFunction() public onlyOwner {
        // Properly protected admin function
    }
    
    // Deposit function
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    // Fallback function to receive Ether
    receive() external payable {
        deposit();
    }
}

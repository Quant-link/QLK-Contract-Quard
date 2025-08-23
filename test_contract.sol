// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title VulnerableContract
 * @dev This contract contains multiple vulnerabilities for testing ContractQuard
 */
contract VulnerableContract {
    mapping(address => uint256) public balances;
    address public owner;
    bool private locked;
    
    event Deposit(address indexed user, uint256 amount);
    event Withdrawal(address indexed user, uint256 amount);
    
    constructor() {
        owner = msg.sender;
    }
    
    // Vulnerability 1: Reentrancy Attack
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance to withdraw");
        
        // External call before state change - VULNERABLE!
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] = 0; // State change after external call
        emit Withdrawal(msg.sender, amount);
    }
    
    // Vulnerability 2: Access Control Issue
    function emergencyWithdraw() public {
        // Missing access control - anyone can call this!
        uint256 contractBalance = address(this).balance;
        payable(msg.sender).transfer(contractBalance);
    }
    
    // Vulnerability 3: Integer Overflow (if using older Solidity)
    function deposit() public payable {
        require(msg.value > 0, "Must send some ether");
        
        // Potential overflow if balances[msg.sender] + msg.value > type(uint256).max
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }
    
    // Vulnerability 4: Unchecked External Call
    function transferTo(address payable recipient, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        balances[msg.sender] -= amount;
        
        // Unchecked external call - VULNERABLE!
        recipient.call{value: amount}("");
        // No check for success/failure
    }
    
    // Vulnerability 5: Timestamp Dependence
    function timeLimitedFunction() public view returns (bool) {
        // Using block.timestamp for critical logic - VULNERABLE!
        return block.timestamp % 2 == 0;
    }
    
    // Vulnerability 6: Unprotected Self-Destruct
    function destroy() public {
        // No access control on self-destruct - VULNERABLE!
        selfdestruct(payable(msg.sender));
    }
    
    // Vulnerability 7: Gas Limit DoS
    function massTransfer(address[] memory recipients, uint256[] memory amounts) public {
        require(recipients.length == amounts.length, "Arrays length mismatch");
        
        // No gas limit check - can cause DoS - VULNERABLE!
        for (uint256 i = 0; i < recipients.length; i++) {
            require(balances[msg.sender] >= amounts[i], "Insufficient balance");
            balances[msg.sender] -= amounts[i];
            balances[recipients[i]] += amounts[i];
        }
    }
    
    // Vulnerability 8: Weak Randomness
    function randomNumber() public view returns (uint256) {
        // Predictable randomness - VULNERABLE!
        return uint256(keccak256(abi.encodePacked(block.timestamp, block.difficulty, msg.sender))) % 100;
    }
    
    // Vulnerability 9: Uninitialized Storage Pointer
    struct User {
        address addr;
        uint256 balance;
        bool active;
    }
    
    User[] public users;
    
    function addUser() public {
        User memory newUser; // Uninitialized - VULNERABLE!
        newUser.addr = msg.sender;
        newUser.balance = 0;
        users.push(newUser);
    }
    
    // Vulnerability 10: Front-running
    function commitReveal(bytes32 commitment) public payable {
        // Simple commit without proper reveal mechanism - VULNERABLE to front-running!
        require(msg.value > 0, "Must send ether");
        balances[msg.sender] += msg.value;
    }
    
    // Helper function to get contract balance
    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }
    
    // Fallback function to receive ether
    receive() external payable {
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }
}

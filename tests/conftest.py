"""
Pytest configuration and fixtures for ContractQuard tests.
"""

import pytest
from pathlib import Path
from contractquard.core.config import Config


@pytest.fixture
def test_config():
    """Provide a test configuration."""
    config = Config()
    config.output.verbose = True
    config.include_test_files = True
    return config


@pytest.fixture
def sample_solidity_code():
    """Provide sample Solidity code for testing."""
    return '''
pragma solidity ^0.8.0;

contract VulnerableContract {
    mapping(address => uint256) public balances;
    
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        balances[msg.sender] = 0;  // State change after external call - reentrancy!
    }
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
}
'''


@pytest.fixture
def test_files_dir(tmp_path):
    """Create a temporary directory with test Solidity files."""
    test_dir = tmp_path / "test_contracts"
    test_dir.mkdir()
    
    # Create a vulnerable contract
    vulnerable_contract = test_dir / "vulnerable.sol"
    vulnerable_contract.write_text('''
pragma solidity ^0.8.0;

contract Vulnerable {
    mapping(address => uint256) balances;
    
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        msg.sender.call{value: amount}("");  // Unchecked call
        balances[msg.sender] = 0;
    }
}
''')
    
    # Create a secure contract
    secure_contract = test_dir / "secure.sol"
    secure_contract.write_text('''
pragma solidity ^0.8.0;

contract Secure {
    mapping(address => uint256) balances;
    
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        balances[msg.sender] = 0;  // State change before external call
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}
''')
    
    return test_dir

#![cfg_attr(not(feature = "std"), no_std)]

use ink_lang as ink;

#[ink::contract]
mod vulnerable_contract {
    use ink_storage::traits::SpreadAllocate;
    use ink_storage::Mapping;

    #[ink(storage)]
    #[derive(SpreadAllocate)]
    pub struct VulnerableContract {
        balances: Mapping<AccountId, Balance>,
        owner: AccountId,
        total_supply: Balance,
    }

    impl VulnerableContract {
        #[ink(constructor)]
        pub fn new() -> Self {
            ink_lang::utils::initialize_contract(|contract: &mut Self| {
                let caller = Self::env().caller();
                contract.owner = caller;
                contract.total_supply = 1000000;
                // Missing proper initialization of balances
            })
        }

        // Panic condition - unwrap without checking
        #[ink(message)]
        pub fn get_balance(&self, account: AccountId) -> Balance {
            self.balances.get(&account).unwrap() // VULNERABLE: can panic!
        }

        // Integer arithmetic without checks
        #[ink(message)]
        pub fn unsafe_add(&self, a: u128, b: u128) -> u128 {
            a + b // VULNERABLE: can overflow
        }

        // Unsafe code block
        #[ink(message)]
        pub fn unsafe_operation(&mut self) {
            unsafe {
                // VULNERABLE: unsafe code without proper validation
                let ptr = &mut self.total_supply as *mut Balance;
                *ptr = 0;
            }
        }

        // Direct storage access without validation
        #[ink(message)]
        pub fn direct_balance_set(&mut self, account: AccountId, amount: Balance) {
            self.balances.insert(&account, &amount); // VULNERABLE: no validation
        }

        // Cross-contract call without error handling
        #[ink(message)]
        pub fn call_external(&self, contract_addr: AccountId) {
            let result = ink_env::call::build_call::<ink_env::DefaultEnvironment>()
                .call_type(ink_env::call::Call::new().callee(contract_addr))
                .exec(); // VULNERABLE: result not checked
        }

        // Array indexing without bounds check
        #[ink(message)]
        pub fn unsafe_array_access(&self, arr: Vec<u32>, index: usize) -> u32 {
            arr[index] // VULNERABLE: can panic on out-of-bounds
        }

        // Assert without proper error handling
        #[ink(message)]
        pub fn unsafe_assert(&self, condition: bool) {
            assert!(condition); // VULNERABLE: can panic
        }

        // Expect with potential panic
        #[ink(message)]
        pub fn unsafe_expect(&self, option: Option<u32>) -> u32 {
            option.expect("Value should exist") // VULNERABLE: can panic
        }
    }
}

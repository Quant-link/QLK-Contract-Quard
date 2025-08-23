package main

import (
	"fmt"
	"github.com/cosmos/cosmos-sdk/types"
	sdk "github.com/cosmos/cosmos-sdk/types"
)

type VulnerableContract struct {
	balances map[string]uint64
	owner    string
}

// Missing error handling
func (vc *VulnerableContract) GetBalance(addr string) uint64 {
	balance, _ := vc.balances[addr] // Ignored error
	return balance
}

// Panic instead of error return
func (vc *VulnerableContract) PanicFunction() {
	panic("Something went wrong") // VULNERABLE: using panic
}

// Missing message validation
func (vc *VulnerableContract) HandleTransferMsg(msg TransferMsg) {
	// No ValidateBasic() call
	// No input validation
	vc.balances[msg.From] -= msg.Amount
	vc.balances[msg.To] += msg.Amount
}

// Missing authorization check
func (vc *VulnerableContract) AdminFunction() {
	// No authorization check - anyone can call this!
	vc.owner = "new_owner"
}

// Unvalidated state transition
func (vc *VulnerableContract) SetState(newState string) {
	// No state validation
	vc.owner = newState
}

// Gas limit issue - unbounded loop
func (vc *VulnerableContract) ProcessLargeArray(arr []uint64) {
	for i := 0; i < len(arr); i++ {
		// Unbounded loop - can run out of gas
		vc.balances["user"] += arr[i]
	}
}

// Array access without bounds checking
func (vc *VulnerableContract) UnsafeArrayAccess(arr []string, index int) string {
	return arr[index] // VULNERABLE: can panic on out-of-bounds
}

// Missing permission check
func (vc *VulnerableContract) GovernanceFunction() {
	// Should check for governance authority
	// But doesn't - VULNERABLE!
	vc.balances = make(map[string]uint64)
}

type TransferMsg struct {
	From   string
	To     string
	Amount uint64
}

// Missing ValidateBasic implementation
func (msg TransferMsg) ValidateBasic() error {
	// Should validate addresses and amounts
	// But implementation is missing
	return nil
}

// Keeper without proper authorization
type VulnerableKeeper struct {
	storeKey sdk.StoreKey
}

func (k VulnerableKeeper) SetBalance(ctx sdk.Context, addr string, amount uint64) {
	// No authorization check - VULNERABLE!
	store := ctx.KVStore(k.storeKey)
	store.Set([]byte(addr), []byte(fmt.Sprintf("%d", amount)))
}

func (k VulnerableKeeper) DeleteAccount(ctx sdk.Context, addr string) {
	// No authorization check - VULNERABLE!
	store := ctx.KVStore(k.storeKey)
	store.Delete([]byte(addr))
}

// Message handler without validation
func HandleVulnerableMsg(ctx sdk.Context, msg VulnerableMsg) error {
	// No input validation
	// No authorization check
	// Direct state modification
	return nil
}

type VulnerableMsg struct {
	Sender string
	Data   []byte
}

func (msg VulnerableMsg) GetSigners() []sdk.AccAddress {
	// Should return proper signers but doesn't validate
	return []sdk.AccAddress{}
}

func main() {
	contract := &VulnerableContract{
		balances: make(map[string]uint64),
		owner:    "initial_owner",
	}
	
	// Demonstrate vulnerabilities
	contract.PanicFunction() // Will panic
}


package atm.bank;

public class SavingsAccount extends Account {
    public SavingsAccount(String id, String customerId, double openingBalance) {
        super(id, customerId, "Savings", openingBalance);
    }
}

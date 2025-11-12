
package atm.bank;

public class CheckingAccount extends Account {
    public CheckingAccount(String id, String customerId, double openingBalance) {
        super(id, customerId, "Checking", openingBalance);
    }
}

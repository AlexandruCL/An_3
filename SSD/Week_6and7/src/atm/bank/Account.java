
package atm.bank;

public abstract class Account {
    private final String id;
    private final String customerId;
    private final String type;
    private double balance;

    protected Account(String id, String customerId, String type, double openingBalance) {
        this.id = id; this.customerId = customerId; this.type = type; this.balance = openingBalance;
    }

    public String getId() { return id; }
    public String getCustomerId() { return customerId; }
    public String getType() { return type; }
    public double getBalance() { return balance; }
    public void setBalance(double balance) { this.balance = balance; }
}

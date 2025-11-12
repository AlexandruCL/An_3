
package atm.transactions;

public class PinChange extends Transaction {
    private final String primaryAccountId;
    public PinChange(String accountId) { super("PIN Change", 0.0); this.primaryAccountId = accountId; }
    public boolean involves(String id) { return primaryAccountId != null && primaryAccountId.equals(id); }
    public String toDisplayString() { return tsFmt()+" | "+type+" | success"; }
}

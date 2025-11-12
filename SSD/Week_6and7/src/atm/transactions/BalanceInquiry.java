
package atm.transactions;

public class BalanceInquiry extends Transaction {
    private final String accountId;
    public BalanceInquiry(String accountId, double dummy) { super("BalanceInquiry", 0.0); this.accountId = accountId; }
    public boolean involves(String id) { return accountId.equals(id); }
    public String toDisplayString() { return tsFmt()+" | "+type+" | acct="+accountId; }
}

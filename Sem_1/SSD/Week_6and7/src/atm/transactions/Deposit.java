
package atm.transactions;

import atm.util.CurrencyUtil;

public class Deposit extends Transaction {
    private final String accountId;
    public Deposit(String accountId, double amount) { super("Deposit", amount); this.accountId = accountId; }
    public boolean involves(String id) { return accountId.equals(id); }
    public String toDisplayString() { return tsFmt()+" | "+type+" | acct="+accountId+" | +"+CurrencyUtil.fmt(amount); }
}

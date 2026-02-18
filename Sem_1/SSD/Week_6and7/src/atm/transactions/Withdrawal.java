
package atm.transactions;

import atm.util.CurrencyUtil;

public class Withdrawal extends Transaction {
    private final String accountId;
    public Withdrawal(String accountId, double amount) { super("Withdrawal", amount); this.accountId = accountId; }
    public boolean involves(String id) { return accountId.equals(id); }
    public String toDisplayString() { return tsFmt()+" | "+type+" | acct="+accountId+" | -"+CurrencyUtil.fmt(amount); }
}

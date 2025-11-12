
package atm.transactions;

import atm.util.CurrencyUtil;

public class Transfer extends Transaction {
    private final String fromId, toId;
    public Transfer(String fromId, String toId, double amount) { super("Transfer", amount); this.fromId=fromId; this.toId=toId; }
    public boolean involves(String id) { return fromId.equals(id) || toId.equals(id); }
    public String toDisplayString() { return tsFmt()+" | "+type+" | "+CurrencyUtil.fmt(amount)+" | "+fromId+" -> "+toId; }
}

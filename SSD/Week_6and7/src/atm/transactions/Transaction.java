
package atm.transactions;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Collection;

public abstract class Transaction {
    protected final String type;
    protected final LocalDateTime ts = LocalDateTime.now();
    protected final double amount;

    protected Transaction(String type, double amount) {
        this.type = type; this.amount = amount;
    }

    public abstract boolean involves(String accountId);
    public boolean involvesAny(Collection<String> accountIds) {
        for (String id : accountIds) if (involves(id)) return true;
        return false;
    }

    protected String tsFmt() { return ts.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")); }
    public abstract String toDisplayString();
}

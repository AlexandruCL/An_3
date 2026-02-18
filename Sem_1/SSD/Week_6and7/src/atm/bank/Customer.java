
package atm.bank;

public class Customer {
    private final String id;
    private final String fullName;
    private final Card card;
    private String primaryAccountId;

    public Customer(String id, String fullName, Card card) {
        this.id = id; this.fullName = fullName; this.card = card;
    }
    public String getId() { return id; }
    public String getFullName() { return fullName; }
    public Card getCard() { return card; }
    public String getPrimaryAccountId() { return primaryAccountId; }
    public void setPrimaryAccountId(String primaryAccountId) { this.primaryAccountId = primaryAccountId; }
}

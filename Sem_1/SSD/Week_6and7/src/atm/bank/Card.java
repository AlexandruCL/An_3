
package atm.bank;

public class Card {
    private final String cardNumber;
    private String pin;
    private boolean active = true;

    public Card(String cardNumber, String pin) { this.cardNumber = cardNumber; this.pin = pin; }
    public String getCardNumber() { return cardNumber; }
    public String getPin() { return pin; }
    public void setPin(String pin) { this.pin = pin; }
    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }
}

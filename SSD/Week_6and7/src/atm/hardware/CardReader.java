
package atm.hardware;

public class CardReader {
    private final Keypad keypad; private final Screen screen; private boolean hasCard = false; private String currentCardNumber;
    public CardReader(Keypad keypad, Screen screen) { this.keypad = keypad; this.screen = screen; }
    public String readCardNumber() {
        String num = keypad.readString("Insert/enter card number (or blank to quit): ").trim();
        if (num.isEmpty()) return null;
        hasCard = true; currentCardNumber = num; return num;
    }
    public void ejectCard() {
        if (hasCard) {
            screen.println("Card ejected.\n");
            hasCard = false; currentCardNumber = null;
        }
    }
}

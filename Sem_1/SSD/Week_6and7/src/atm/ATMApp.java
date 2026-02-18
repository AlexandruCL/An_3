
package atm;

import atm.bank.Bank;
import atm.hardware.*;
import atm.util.DemoDataFactory;

public class ATMApp {
    public static void main(String[] args) {
        Screen screen = new Screen();
        Keypad keypad = new Keypad();
        CardReader cardReader = new CardReader(keypad, screen);
        CashDispenser dispenser = new CashDispenser(50, 50, 50, 50);
        ReceiptPrinter printer = new ReceiptPrinter(screen);

        Bank bank = DemoDataFactory.sampleBank();
        ATM atm = new ATM(bank, screen, keypad, cardReader, dispenser, printer);
        atm.start();
    }
}

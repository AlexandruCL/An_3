
package atm;

import atm.bank.*;
import atm.hardware.*;
import atm.transactions.*;
import atm.util.*;

import java.util.*;

public class ATM {
    private final Bank bank;
    private final Screen screen;
    private final Keypad keypad;
    private final CardReader cardReader;
    private final CashDispenser dispenser;
    private final ReceiptPrinter printer;

    public ATM(Bank bank, Screen screen, Keypad keypad, CardReader cardReader,
               CashDispenser dispenser, ReceiptPrinter printer) {
        this.bank = bank;
        this.screen = screen;
        this.keypad = keypad;
        this.cardReader = cardReader;
        this.dispenser = dispenser;
        this.printer = printer;
    }

    public void start() {
        powerOn();
        run();
    }

    private void powerOn() {
        screen.println("ATM starting up...\n");
    }

    private void run() {
        while (true) {
            screen.hr();
            screen.title("Welcome to DemoBank ATM");
            String cardNumber = cardReader.readCardNumber();
            if (cardNumber == null) {
                screen.println("No card detected. Exiting.");
                return;
            }
            Optional<Session> sessionOpt = authenticate(cardNumber);
            if (sessionOpt.isEmpty()) {
                cardReader.ejectCard();
                continue;
            }
            Session session = sessionOpt.get();
            mainMenu(session);
            cardReader.ejectCard();
        }
    }

    private Optional<Session> authenticate(String cardNumber) {
        if (!bank.cardExists(cardNumber)) {
            screen.println("Unknown card number.");
            return Optional.empty();
        }
        int attempts = 0;
        while (attempts < 3) {
            String pin = keypad.readPIN("Enter PIN: ");
            if (bank.verifyPIN(cardNumber, pin)) {
                screen.println("Authentication successful.\n");
                return Optional.of(new Session(bank.getCustomerByCard(cardNumber)));
            } else {
                attempts++;
                screen.println("Invalid PIN (" + attempts + "/3).\n");
            }
        }
        screen.println("Too many invalid attempts. Card locked.");
        bank.lockCard(cardNumber);
        return Optional.empty();
    }

    private void mainMenu(Session session) {
        boolean keepGoing = true;
        while (keepGoing) {
            screen.hr();
            screen.title("Main Menu - " + session.customer().getFullName());
            screen.println("1) Balance inquiry");
            screen.println("2) Cash withdrawal");
            screen.println("3) Deposit");
            screen.println("4) Transfer");
            screen.println("5) Mini statement");
            screen.println("6) Change PIN");
            screen.println("0) Exit");
            int choice = keypad.readInt("Choose an option: ");
            try {
                switch (choice) {
                    case 1 -> doBalance(session);
                    case 2 -> doWithdrawal(session);
                    case 3 -> doDeposit(session);
                    case 4 -> doTransfer(session);
                    case 5 -> doMiniStatement(session);
                    case 6 -> doChangePIN(session);
                    case 0 -> { keepGoing = false; screen.println("Goodbye!\n"); }
                    default -> screen.println("Invalid option.\n");
                }
            } catch (ATMError e) {
                screen.println("Error: " + e.getMessage());
            }
        }
    }

    private void doBalance(Session session) {
        Account acct = selectAccount(session, "Select account for balance inquiry");
        double bal = bank.getBalance(acct.getId());
        screen.println("Current balance: " + CurrencyUtil.fmt(bal));
        bank.logTransaction(new BalanceInquiry(acct.getId(), 0.0));
        java.util.Map<String,String> lines = new java.util.LinkedHashMap<>();
        lines.put("Account", acct.getId());
        lines.put("Balance", CurrencyUtil.fmt(bal));
        printer.printReceipt("Balance Inquiry", lines);
    }

    private void doWithdrawal(Session session) {
        Account acct = selectAccount(session, "Select account for withdrawal");
        double amount = keypad.readDouble("Amount to withdraw: ");
        if (amount <= 0) throw new ATMError("Amount must be positive.");
        if (!dispenser.canDispense(amount)) throw new ATMError("ATM cannot dispense that amount with available notes.");
        bank.withdraw(acct.getId(), amount);
        dispenser.dispense(amount);
        bank.logTransaction(new Withdrawal(acct.getId(), amount));
        java.util.Map<String,String> lines = new java.util.LinkedHashMap<>();
        lines.put("Account", acct.getId());
        lines.put("Amount", CurrencyUtil.fmt(amount));
        lines.put("Remaining Balance", CurrencyUtil.fmt(bank.getBalance(acct.getId())));
        printer.printReceipt("Cash Withdrawal", lines);
    }

    private void doDeposit(Session session) {
        Account acct = selectAccount(session, "Select account for deposit");
        double amount = keypad.readDouble("Amount to deposit: ");
        if (amount <= 0) throw new ATMError("Amount must be positive.");
        bank.deposit(acct.getId(), amount);
        bank.logTransaction(new Deposit(acct.getId(), amount));
        java.util.Map<String,String> lines = new java.util.LinkedHashMap<>();
        lines.put("Account", acct.getId());
        lines.put("Amount", CurrencyUtil.fmt(amount));
        lines.put("New Balance", CurrencyUtil.fmt(bank.getBalance(acct.getId())));
        printer.printReceipt("Deposit", lines);
    }

    private void doTransfer(Session session) {
        Account from = selectAccount(session, "Select FROM account");
        Account to = selectAccount(session, "Select TO account");
        if (from.getId().equals(to.getId())) throw new ATMError("Source and destination cannot be the same.");
        double amount = keypad.readDouble("Amount to transfer: ");
        if (amount <= 0) throw new ATMError("Amount must be positive.");
        bank.transfer(from.getId(), to.getId(), amount);
        bank.logTransaction(new Transfer(from.getId(), to.getId(), amount));
        java.util.Map<String,String> lines = new java.util.LinkedHashMap<>();
        lines.put("From", from.getId());
        lines.put("To", to.getId());
        lines.put("Amount", CurrencyUtil.fmt(amount));
        lines.put("From Balance", CurrencyUtil.fmt(bank.getBalance(from.getId())));
        lines.put("To Balance", CurrencyUtil.fmt(bank.getBalance(to.getId())));
        printer.printReceipt("Transfer", lines);
    }

    private void doMiniStatement(Session session) {
        java.util.List<Transaction> txs = bank.getRecentTransactions(session.customer().getId(), 10);
        screen.title("Last " + txs.size() + " transaction(s)");
        for (Transaction t : txs) {
            screen.println(t.toDisplayString());
        }
    }

    private void doChangePIN(Session session) {
        String oldPin = keypad.readPIN("Enter current PIN: ");
        if (!bank.verifyPIN(session.customer().getCard().getCardNumber(), oldPin))
            throw new ATMError("Current PIN incorrect.");
        String newPin = keypad.readPIN("Enter new 4-digit PIN: ");
        if (!newPin.matches("\\d{4}")) throw new ATMError("PIN must be exactly 4 digits.");
        String confirm = keypad.readPIN("Re-enter new PIN: ");
        if (!newPin.equals(confirm)) throw new ATMError("PINs do not match.");
        bank.changePIN(session.customer().getId(), newPin);
        bank.logTransaction(new PinChange(session.customer().getPrimaryAccountId()));
        java.util.Map<String,String> lines = new java.util.LinkedHashMap<>();
        lines.put("Status", "Success");
        printer.printReceipt("PIN Change", lines);
        screen.println("PIN changed successfully.\n");
    }

    private Account selectAccount(Session session, String title) {
        java.util.List<Account> accounts = bank.getAccountsByCustomer(session.customer().getId());
        if (accounts.isEmpty()) throw new ATMError("No accounts available.");
        screen.title(title);
        for (int i = 0; i < accounts.size(); i++) {
            Account a = accounts.get(i);
            screen.println((i + 1) + ") " + a.getId() + " [" + a.getType() + "] - Balance: " + CurrencyUtil.fmt(a.getBalance()));
        }
        int idx = keypad.readInt("Choose (1-" + accounts.size() + "): ") - 1;
        if (idx < 0 || idx >= accounts.size()) throw new ATMError("Invalid selection.");
        return accounts.get(idx);
    }
}

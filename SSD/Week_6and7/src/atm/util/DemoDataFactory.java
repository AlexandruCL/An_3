
package atm.util;

import atm.bank.*;
import atm.transactions.*;

import java.util.UUID;

public class DemoDataFactory {
    public static Bank sampleBank() {
        Bank bank = new Bank();
        Customer alice = new Customer(uid(), "Alice Johnson", new Card("1111-2222-3333-4444", "1234"));
        Customer bob   = new Customer(uid(), "Bob Smith", new Card("5555-6666-7777-8888", "4321"));

        bank.addCustomer(alice); bank.addCustomer(bob);

        Account a1 = new CheckingAccount("CHK-1001", alice.getId(), 1250.00);
        Account a2 = new SavingsAccount("SAV-1002", alice.getId(), 5400.00);
        Account b1 = new CheckingAccount("CHK-2001", bob.getId(), 300.00);

        bank.addAccount(a1); bank.addAccount(a2); bank.addAccount(b1);

        alice.setPrimaryAccountId(a1.getId());
        bob.setPrimaryAccountId(b1.getId());

        bank.logTransaction(new Deposit(a1.getId(), 200));
        bank.logTransaction(new Withdrawal(a1.getId(), 50));
        bank.logTransaction(new Transfer(a1.getId(), a2.getId(), 100));

        return bank;
    }

    private static String uid() { return UUID.randomUUID().toString(); }
}

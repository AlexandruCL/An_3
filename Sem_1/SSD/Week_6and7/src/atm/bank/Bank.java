
package atm.bank;

import atm.transactions.*;
import atm.util.ATMError;

import java.util.*;

public class Bank {
    private final Map<String, Customer> customersById = new HashMap<>();
    private final Map<String, Account> accountsById = new HashMap<>();
    private final Map<String, String> cardToCustomerId = new HashMap<>();
    private final Deque<Transaction> auditLog = new ArrayDeque<>();

    public void addCustomer(Customer c) {
        customersById.put(c.getId(), c);
        cardToCustomerId.put(c.getCard().getCardNumber(), c.getId());
    }
    public void addAccount(Account a) { accountsById.put(a.getId(), a); }

    public boolean cardExists(String cardNumber) {
        return cardToCustomerId.containsKey(cardNumber);
    }

    public Customer getCustomerByCard(String cardNumber) {
        return customersById.get(cardToCustomerId.get(cardNumber));
    }

    public boolean verifyPIN(String cardNumber, String pin) {
        String cid = cardToCustomerId.get(cardNumber);
        if (cid == null) return false;
        Customer c = customersById.get(cid);
        if (c == null) return false;
        return c.getCard().isActive() && c.getCard().getPin().equals(pin);
    }

    public void lockCard(String cardNumber) {
        String cid = cardToCustomerId.get(cardNumber);
        if (cid == null) return;
        customersById.get(cid).getCard().setActive(false);
    }

    public List<Account> getAccountsByCustomer(String customerId) {
        List<Account> res = new ArrayList<>();
        for (Account a : accountsById.values()) {
            if (a.getCustomerId().equals(customerId)) res.add(a);
        }
        res.sort(Comparator.comparing(Account::getId));
        return res;
    }

    public double getBalance(String accountId) {
        return getAccountOrThrow(accountId).getBalance();
    }

    public void withdraw(String accountId, double amount) {
        Account a = getAccountOrThrow(accountId);
        if (a.getBalance() < amount) throw new ATMError("Insufficient funds.");
        a.setBalance(a.getBalance() - amount);
    }

    public void deposit(String accountId, double amount) {
        Account a = getAccountOrThrow(accountId);
        a.setBalance(a.getBalance() + amount);
    }

    public void transfer(String fromId, String toId, double amount) {
        if (amount <= 0) throw new ATMError("Amount must be positive.");
        Account from = getAccountOrThrow(fromId);
        Account to = getAccountOrThrow(toId);
        if (from.getBalance() < amount) throw new ATMError("Insufficient funds.");
        from.setBalance(from.getBalance() - amount);
        to.setBalance(to.getBalance() + amount);
    }

    public void changePIN(String customerId, String newPin) {
        Customer c = customersById.get(customerId);
        if (c == null) throw new ATMError("Customer not found.");
        c.getCard().setPin(newPin);
    }

    public void logTransaction(Transaction t) {
        auditLog.addFirst(t);
        while (auditLog.size() > 500) auditLog.removeLast();
    }

    public List<Transaction> getRecentTransactions(String customerId, int max) {
        List<String> acctIds = new ArrayList<>();
        for (Account a : getAccountsByCustomer(customerId)) acctIds.add(a.getId());
        List<Transaction> res = new ArrayList<>();
        for (Transaction t : auditLog) {
            if (t.involvesAny(acctIds)) res.add(t);
            if (res.size() >= max) break;
        }
        Collections.reverse(res);
        return res;
    }

    private Account getAccountOrThrow(String id) {
        Account a = accountsById.get(id);
        if (a == null) throw new ATMError("Account not found: " + id);
        return a;
    }
}

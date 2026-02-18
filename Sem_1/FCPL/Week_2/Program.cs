using System.Security.Principal;
using System.Collections.Generic;
using System;
using System.Runtime.InteropServices.Swift;

namespace BankSystem
{
    public enum AccountType

    {
        Person,
        Company
    }

    public class Account
    {
        public readonly string AccountHolder;
        public readonly AccountType Type;
        public readonly string Iban;
        public decimal Amount { get; private set; }

        public Account(string accountHolder, AccountType type, string iban, decimal amount)
        {
            AccountHolder = accountHolder;
            Type = type;
            Iban = iban;
            Amount = amount;
        }
        public void Deposit(decimal amount)
        {
            if (amount <= 0)
            {
                Console.WriteLine("Deposit amount must be positive.");
                return;
            }
            Amount += amount;
            Console.WriteLine($"Deposited {amount:C} to account {Iban}. New balance: {Amount:C}");
        }
        public void Withdraw(decimal amount)
        {
            if (amount <= 0)
            {
                Console.WriteLine("Withdrawal amount must be positive.");
                return;
            }
            if (amount > Amount)
            {
                Console.WriteLine("Insufficient funds for this withdrawal.");
                return;
            }
            Amount -= amount;
            Console.WriteLine($"Withdrew {amount:C} from account {Iban}. New balance: {Amount:C}");
        }
        public override string ToString()
        {
            return $"Account Holder: {AccountHolder}\n" +
                   $"Account Type: {Type}\n" +
                   $"IBAN: {Iban}\n" +
                   $"Balance: {Amount:C}\n";
        }
    }

    public class Bank
    {
        public readonly String Name;
        public readonly String Swift;
        public readonly List<Account> Accounts;

        public Bank(string name, string swift)
        {
            Name = name;
            Swift = swift;
            Accounts = new List<Account>();
        }
        private Account? GetAccountByIban(string iban)
        {
            foreach (var account in Accounts)
            {
                if (account.Iban == iban)
                {
                    return account;
                }
            }
            return null;
        }
        public void OpenAccount(string accountHolder, AccountType type, string iban, decimal initialDeposit)
        {
            if (GetAccountByIban(iban) != null)
            {
                Console.WriteLine("An account with this IBAN already exists.");
                return;
            }
            if (initialDeposit < 0)
            {
                Console.WriteLine("Initial deposit must be non-negative.");
                return;
            }
            Accounts.Add(new Account(accountHolder, type, iban, initialDeposit));
            Console.WriteLine($"Account {iban} opened successfully for {accountHolder} with initial deposit of {initialDeposit:C}.");
        }
        public void DisplayAccount(string iban)
        {
            var account = GetAccountByIban(iban);
            if (account == null)
            {
                Console.WriteLine("Account with iban : { " + iban + " } not found.");
                return;
            }
            Console.WriteLine(account);
        }
        public void Deposit(string iban, decimal amount)
        {
            var account = GetAccountByIban(iban);
            if (account == null)
            {
                Console.WriteLine("Account not found.");
                return;
            }
            if (amount <= 0)
            {
                Console.WriteLine("Deposit amount must be positive.");
                return;
            }
            account.Deposit(amount);
        }

        public void Withdraw(string iban, decimal amount)
        {
            var account = GetAccountByIban(iban);
            if (account == null)
            {
                Console.WriteLine("Account not found.");
                return;
            }
            if( amount > account.Amount)
            {
                Console.WriteLine("Insufficient funds for this withdrawal.");
                return;
            }
            account.Withdraw(amount);
        }
        public void Transfer(string fromIban, string toIban, decimal amount)
        {
            var fromAccount = GetAccountByIban(fromIban);
            var toAccount = GetAccountByIban(toIban);
            if (fromAccount == null && toAccount == null)
            {
                Console.WriteLine("Both accounts were not found.");
                return;
            }
            else if (fromAccount == null)
            {
                Console.WriteLine("The account to transfer from was not found.");
                return;
            }
            else if (toAccount == null)
            {
                Console.WriteLine("The account to transfer to was not found.");
                return;
            }

            if (fromAccount.Amount < amount)
            {
                Console.WriteLine("Insufficient funds for this transfer.");
                return;
            }
            if (fromAccount == toAccount)
            {
                Console.WriteLine("Cannot transfer to the same account.");
                return;
            }
            fromAccount.Withdraw(amount);
            toAccount.Deposit(amount);
            Console.WriteLine($"Transferred {amount:C} from {fromIban} to {toIban}.");
        }
    }
    class Program
    {
        static void Main(string[] args)
        {
            Bank bank = new Bank("MyBank", "MYBKUS33");

            Console.WriteLine($"Welcome to {bank.Name} (SWIFT: {bank.Swift})");
            Console.WriteLine("Account Openings: \n");

            bank.OpenAccount("Alice", AccountType.Person, "US1234567890", 1000);
            bank.OpenAccount("Bob's Burgers", AccountType.Company, "US0987654321", 5000);
            bank.OpenAccount("Charlie", AccountType.Person, "US1234567890", 300); //should fail
            bank.OpenAccount("Dave", AccountType.Person, "US1111111111", -100); //should fail

            Console.WriteLine("\nAccounts Display:\n");

            bank.DisplayAccount("US1234567890");
            bank.DisplayAccount("US0987654321");
            bank.DisplayAccount("US1111111111");//should fail

            Console.WriteLine("\nTransactions:\n");

            bank.Deposit("US1234567890", 200);
            bank.Deposit("US0987654321", -50); //should fail
            bank.Withdraw("US0987654321", 1000);
            bank.Withdraw("US1234567890", 5000); //should fail

            Console.WriteLine("\nAfter Transactions:\n");

            bank.DisplayAccount("US1234567890");//should see 1200
            bank.DisplayAccount("US0987654321");//should see 4000

            Console.WriteLine("\nTransfers between Accounts:\n");

            bank.Transfer("US1234567890", "US0987654321", 300);
            bank.Transfer("US1234567890", "US0987654321", 50000); //should fail
            bank.Transfer("US1234567890", "Uss1234567890", 100); //should fail

            Console.WriteLine("\nAfter Transfers:\n");

            bank.DisplayAccount("US1234567890");//should see 900
            bank.DisplayAccount("US0987654321");//should see 4300
        }
    }
}

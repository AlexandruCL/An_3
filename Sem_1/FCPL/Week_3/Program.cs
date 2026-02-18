using System;
using System.Collections;
using System.ComponentModel;


class Problem1
{
    public static void Swap(ref int a, ref int b)
    {
        int temp = a;
        a = b;
        b = temp;
    }
}

class Problem2
{
    public struct Coords
    {
        public float X { get; set; }
        public float Y { get; set; }

        public Coords(float x, float y)
        {
            X = x;
            Y = y;
        }

        public override string ToString()
        {
            return $"({X}, {Y})";
        }
    }

    public static Coords MiddleCoord(Coords point1, Coords point2)
    {
        float middleX = (point1.X + point2.X) / 2;
        float middleY = (point1.Y + point2.Y) / 2;
        return new Coords(middleX, middleY);
    }
}

class Account
{
    private string name { get; set; }
    private decimal balance { get; set; }

    public Account(string name, decimal balance)
    {
        this.name = name;
        this.balance = balance;
    }

    public bool Withdraw(double amount, out double remainingBalance)
    {
        if (amount <= 0)
        {
            Console.WriteLine("Withdrawal amount must be positive.");
            remainingBalance = (double)balance;
            return false;
        }
        if (amount > (double)balance)
        {
            Console.WriteLine("Insufficient funds.");
            remainingBalance = (double)balance;
            return false;
        }
        if (amount == (double)balance)
        {
            Console.WriteLine("You withdrawed all your money.");
            balance = 0;
            remainingBalance = (double)balance;
            return true;
        }
        balance -= (decimal)amount;
        remainingBalance = (double)balance;
        return true;
    }
}
class Program
{
    static void Main(string[] args)
    {
        int stop = -1;
        while (stop != 0)
        {
            Console.Write("Enter the exercise number: (0 to stop the program) ");
            int exercise = int.TryParse(Console.ReadLine(), out int result) ? result : throw new FormatException("Invalid input. Please enter a valid integer.");
            switch (exercise)
            {
                case 1:
                    Console.Write("Enter x: ");
                    int x = int.TryParse(Console.ReadLine(), out int xResult) ? xResult : throw new FormatException("Invalid input. Please enter a valid integer.");
                    Console.Write("Enter y: ");
                    int y = int.TryParse(Console.ReadLine(), out int yResult) ? yResult : throw new FormatException("Invalid input. Please enter a valid integer.");
                    Console.WriteLine($"Before Swap: x = {x}, y = {y}");
                    Problem1.Swap(ref x, ref y);
                    Console.WriteLine($"After Swap: x = {x}, y = {y}");
                    break;
                case 2:
                    Console.Write("Enter x1: ");
                    float x1 = float.TryParse(Console.ReadLine(), out float x1Result) ? x1Result : throw new FormatException("Invalid input. Please enter a valid number.");
                    Console.Write("Enter y1: ");
                    float y1 = float.TryParse(Console.ReadLine(), out float y1Result) ? y1Result : throw new FormatException("Invalid input. Please enter a valid number.");
                    Console.Write("Enter x2: ");
                    float x2 = float.TryParse(Console.ReadLine(), out float x2Result) ? x2Result : throw new FormatException("Invalid input. Please enter a valid number.");
                    Console.Write("Enter y2: ");
                    float y2 = float.TryParse(Console.ReadLine(), out float y2Result) ? y2Result : throw new FormatException("Invalid input. Please enter a valid number.");
                    Problem2.Coords point1 = new Problem2.Coords(x1, y1);
                    Problem2.Coords point2 = new Problem2.Coords(x2, y2);
                    Problem2.Coords middlePoint = Problem2.MiddleCoord(point1, point2);
                    Console.WriteLine($"Middle Point: {middlePoint}");
                    break;
                case 3:
                    Console.Write("Enter account name: ");
                    string name = Console.ReadLine() ?? throw new ArgumentNullException("Account name cannot be null.");
                    Console.Write("Enter initial balance: ");
                    decimal balance = decimal.TryParse(Console.ReadLine(), out decimal balanceResult) ? balanceResult : throw new FormatException("Invalid input. Please enter a valid decimal number.");
                    Account account = new Account(name, balance);
                    Console.WriteLine($"Account created for {name} with initial balance {balance}");
                    bool stopEx3 = false;
                    while (stopEx3 == false)
                    {
                        Console.Write("Enter amount to withdraw(enter -1 to stop the program):  ");
                        double amount = double.TryParse(Console.ReadLine(), out double amountResult) ? amountResult : throw new FormatException("Invalid input. Please enter a valid number.");
                        if (amount == -1)
                            break;
                        if (account.Withdraw(amount, out double remainingBalance))
                        {
                            Console.WriteLine($"Withdrawal successful. Remaining balance: {remainingBalance}");
                        }
                        else
                        {
                            Console.WriteLine($"Withdrawal failed. Remaining balance: {remainingBalance}");
                        }
                        Console.WriteLine("After withdrawal account information: \n" +
                                        $"Name: {name}\n" +
                                        $"Balance: {remainingBalance}");
                    }
                    break;
                case 0:
                    stop = 0;
                    Console.WriteLine("Exiting the program.");
                    break;
                default:
                    Console.WriteLine("Exercise not found.");
                    break;
            }
        }
    }
}
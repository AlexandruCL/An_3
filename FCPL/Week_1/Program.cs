using System;

class Program
{
    public static void SumOfNumbers()
    {
        Console.Write("Enter how many numbers you want to input:");
        int count = int.Parse(Console.ReadLine());
        int sum = 0;

        for (int i = 0; i < count; i++)
        {
            Console.Write($"Enter number {i + 1}:");
            int number = int.Parse(Console.ReadLine());
            sum += number;
        }

        Console.WriteLine($"The sum of the entered numbers is: {sum}");
    }

    public static void SecondGradeEquation()
    {
        Console.Write("Enter coefficient a: ");
        double a = double.Parse(Console.ReadLine());
        Console.Write("Enter coefficient b: ");
        double b = double.Parse(Console.ReadLine());
        Console.Write("Enter coefficient c: ");
        double c = double.Parse(Console.ReadLine());

        double discriminant = b * b - 4 * a * c;

        if (discriminant > 0)
        {
            double root1 = (-b + Math.Sqrt(discriminant)) / (2 * a);
            double root2 = (-b - Math.Sqrt(discriminant)) / (2 * a);
            Console.WriteLine($"Two distinct real roots: {root1} and {root2}");
        }
        else if (discriminant == 0)
        {
            double root = -b / (2 * a);
            Console.WriteLine($"One real root: {root}");
        }
        else
        {
            Console.WriteLine("No real roots.");
        }
    }

    static void Main()
    {
        Console.Write("What excercise do you want to run?");
        int excercise = int.Parse(Console.ReadLine());
        switch (excercise)
        {
            case 1:
                SumOfNumbers();
                break;
            case 2:
                SecondGradeEquation();
                break;
            case 3:
                Student.StudentProblem();
                break; 
            default:
                Console.WriteLine("Invalid excercise number.");
                break;
        }
    }
}

public class Student
{
    public string Name { get; }
    public int Year { get; }
    public double Grade1 { get; }
    public double Grade2 { get; }
    public double Grade3 { get; }

    public double Average => (Grade1 + Grade2 + Grade3) / 3.0;

    public Student(string name, int year, double grade1, double grade2, double grade3)
    {
        if (string.IsNullOrWhiteSpace(name)) throw new ArgumentException("Name is required.", nameof(name));
        if (year <= 0) throw new ArgumentOutOfRangeException(nameof(year), "Year must be positive.");

        Name = name;
        Year = year;
        Grade1 = grade1;
        Grade2 = grade2;
        Grade3 = grade3;
    }

    public override string ToString()
    {
        return $"{Name}, Year {Year}, Grades: {Grade1:F2}, {Grade2:F2}, {Grade3:F2}, Average: {Average:F2}";
    }

    public static void StudentProblem()
    {
        Console.Write("Enter the number of students: ");
                int n = int.Parse(Console.ReadLine());
                Student[] students = new Student[n];

                for (int i = 0; i < n; i++)
                {
                    Console.WriteLine($"Enter details for student {i + 1}:");
                    Console.Write("Name: ");
                    string name = Console.ReadLine();
                    Console.Write("Year: ");
                    int year = int.Parse(Console.ReadLine());
                    Console.Write("Grade 1: ");
                    double grade1 = double.Parse(Console.ReadLine());
                    Console.Write("Grade 2: ");
                    double grade2 = double.Parse(Console.ReadLine());
                    Console.Write("Grade 3: ");
                    double grade3 = double.Parse(Console.ReadLine());

                    students[i] = new Student(name, year, grade1, grade2, grade3);
                }

                Student topStudent = students[0];
                foreach (var student in students)
                {
                    if (student.Average > topStudent.Average)
                    {
                        topStudent = student;
                    }
                }

                Console.WriteLine("Student with the highest average grade:");
                Console.WriteLine(topStudent);
    }
}

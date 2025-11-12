// 1. A

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public void printSomePoints(List<Point> points) {
    int printedPoints = 0;
    for (Point point : points) {
        if (someCondition()) {
            System.out.println(String.format("Point %d (%f,%f)",
                    printedPoints, point.getX(), point.getY()));
        }
    }
}

class Point {
    private double x;
    private double y;
    // getters and setters
}

// In the printSomePoints method we only access the getters of the given
// parameters, so the method calls only on its direct friends. Therefor, it
// doesn't violate the law

// 1. B

public void printDistanceBetweenRandomPointsOfTwoSquares(Square s1, Square s2) {
    Point randomPoint1 = s1.getRandomPoint();
    Point randomPoint2 = s2.getRandomPoint();
    System.out.println(randomPoint1.distanceTo(randomPoint2));
}

@AllArgsConstructor
class Point {
    @Getter
    private double x;
    @Getter
    private double y;

    public double distanceTo(Point p) {
        return Math.hypot(x - p.x, y - p.y);
    }
}

@Data // getters and setters
@AllArgsConstructor
class Square {
    private Point[] points = new Point[4];

    public Point getRandomPoint() {
        int index = (int) (Math.random() * 4);
        return points[index];
    }
}

// The printDistanceBetweenRandomPointsOfTwoSquares method has two parameters
// (friends): s1 and s2.
// Point randomPoint1 = s1.getRandomPoint();
// Point randomPoint2 = s2.getRandomPoint();
// Here, the method talks to its friend s1... but it "asks" for one of s1's
// internal parts (a Point object).
// System.out.println(randomPoint1.distanceTo(randomPoint2));
// The method then talks directly to that "friend of a friend" (randomPoint1) by
// calling its distanceTo method.
// This is a violation because the printDistance method is reaching through the
// Square object to get one of its internal components (point)
// than calls a method on that component.

public void printDistanceBetweenRandomPointsOfTwoSquares(Square s1, Square s2) {
    double distance = s1.calculateDistanceToRandomPointOf(s2);
    System.out.println(distance);
}

@Data // getters and setters
@AllArgsConstructor
class Square {
    private Point[] points = new Point[4];

    public Point getRandomPoint() {
        int index = (int) (Math.random() * 4);
        return points[index];
    }

    // This new method follows the LoD
    // It only talks to itself (this.) part and its param (other.) part
    public double calculateDistanceToRandomPointOf(Square other) {
        Point p1 = this.getRandomPoint(); // Talk to self
        Point p2 = other.getRandomPoint(); // Talk to param

        return p1.distanceTo(p2); // Talk to locally obtained obj
    }
}

// 1. C

public void someMethod(Student student) {
    Faculty faculty = student.getFaculty();
    System.out.println(faculty.getName());
    System.out.println(faculty.getStudentNo());
}

@Data
@AllArgsConstructor
class Student {
    private String name;
    private Faculty faculty;
}

@Data
@AllArgsConstructor
class Faculty {
    private List<Student> students;

    public int getStudentNo() {
        return students.size();
    }

    public void removeStudent(Student student) {
        students.remove(student);
    }

    public void addStudent(Student student) {
        students.add(student);
    }
}

// In someMethod we receive as a parameter an object of type Student.
// Through it we access a getter to get those students faculty, but then we
// access through another getter
// that faculty’s name and students no. This violates LoD .

public void someMethod(Student student) {
    // This fixes the LoD violation because you only call the param
    System.out.println(student.getFacultyName());
    System.out.println(student.getFacultyStudentNo());
}

@Data
@AllArgsConstructor
class Student {
    private String name;
    private Faculty faculty;

    public String getFacultyName() {
        // Not a violation because student is talking to a friend (faculty)

        return this.faculty.getName();
    }

    public int getFacultyStudentNo() {
        // same as above
        return this.faculty.getStudentNo();
    }
}

@Data
@AllArgsConstructor
class Faculty {
    private List<Student> students;

    public int getStudentNo() {
        return students.size();
    }

    public void removeStudent(Student student) {
        students.remove(student);
    }

    public void addStudent(Student student) {
        students.add(student);
    }
}

// 1. D

public void someMethod() {
    // ...some code
    Student student = Student.builder()
            .lastName("LN")
            .firstName("FN")
            .age(20)
            .bestFriend(null)
            .build();
    System.out.println(student);
    // ...some other code
}

@AllArgsConstructor
class Student {
    private String firstName;
    private String lastName;
    private Integer age;
    private Student bestFriend;

    public static StudentBuilder builder() {
        return new StudentBuilder();
    }
}

class StudentBuilder {
    private String firstName;
    private String lastName;
    private Integer age;
    private Student bestFriend;

    StudentBuilder() {
    }

    public StudentBuilder firstName(String firstName) {
        this.firstName = firstName;
        return this;
    }

    public StudentBuilder lastName(String lastName) {
        this.lastName = lastName;
        return this;
    }

    public StudentBuilder age(Integer age) {
        this.age = age;
        return this;
    }

    public StudentBuilder bestFriend(Student bestFriend) {
        this.bestFriend = bestFriend;
        return this;
    }

    public Student build() {
        return new Student(firstName,
                lastName, age, bestFriend);
    }
}

// This one respects the LoD because Student interacts directly wih
// StudentBuilder. We only have one relation between those 2 classes

// 2.
// A data structure is a method /way to store data and organize it. A class
// combines
// data and behavior by using it in specific methods. LoD applies specifically
// to the relations
// between objects. From what we know, data structures don’t provide information
// about
// relations between objects, so LoD applies mainly on classes.

// ==========================================================================
// S.O.L.I.D
// ==========================================================================

// 1.

// public static Collection readLinesFromFile(String absoluteFilePath)

// Preconditions: absoluteFilePath != null -must not be null, must be a text
// file that can be
// read line by line, valid path to an existing file, at OS level, the file
// should be readable(permission)
// Postconditions: A Collection should be returned, Empty File=Empty Collection
// returned,
// the collection should contain all lines from the specified file in the order
// they were
// read, throw exception if any precondition is violated
// Invariants: absoluteFilePath – is not modified (being read-only), also the
// string itself is not modified
// Side effects: A file handle (input stream) is opened and subsequently closed;
// Memory is
// allocated to store the Collection and all the String objects for the lines
// read, the
// operating system might update “last access time” of the file.

// 2.

// It violates The Interface Segregation Principle(ISP). The client should not
// be forced
// to depend on methods they don’t use . We call IMembership a “fat” interface .
// I would refactor the code by breaking the interface into smaller (more
// role-based/specific focused) interfaces.

// Separate interface for authentication
interface IAuthentication {
    void login(UserCredentials uc);

    boolean logout();
}

// Separate interface for registration
interface IRegistration {
    UserCredentials register(String userName, String password);
}

// Separate interface for password management
interface IPasswordManagement {
    UserCredentials changePassword(String userName);
}

// Separate interface for payment
interface IPaymentManagement {
    void addPaymentMethod(UserCredentials uc, PaymentMethod pm);
}

// If a class needs multiple functionalities, it can implement multiple
// interfaces
class FullMembershipService implements IAuthentication, IRegistration,
        IPasswordManagement, IPaymentManagement {
    @Override
    public void login(UserCredentials uc) {
        /* implementation */ }

    @Override
    public boolean logout() {
        /* implementation */ }

    @Override
    public UserCredentials register(String userName, String password) {
        /* implementation */ }

    @Override
    public UserCredentials changePassword(String userName) {
        /* implementation */ }

    @Override
    public void addPaymentMethod(UserCredentials uc, PaymentMethod pm) {
        /* implementation */ }
}

// But a simple authentication service only implements what it needs
class SimpleAuthService implements IAuthentication {
    @Override
    public void login(UserCredentials uc) {
        /* implementation */ }

    @Override
    public boolean logout() {
        /* implementation */ }
}

// 3.

// String Base :: aMethod(int[] args)
// PRECONDITIONS: args contains only negative numbers
// POSTCONDITIONS: returns a String with only lowercase characters or digits

// ^
// |
// |

// String Derived :: aMethod(int[] args)
// //PRECONDITIONS: args contains any negative or even numbers
// //POSTCONDITIONS: returns a String composed only of digits or null

// This violates the Liskov Substitution Principle. The idea is that
// preconditions can be weaker
// (accept more inputs) , but postconditions must be stronger ( this means that
// guarantees
// more, or at least the same).

// After analyzing preconditions: The derived 1 accepts everything the base does
// (negative
// numbers) + even numbers. This part is correct. The problem is at
// postconditions.

// After analyzing postconditions: The derived postcondition is weaker than
// base’s. Base
// contract guarantees receiving a valid, NON-NULL string of lowercase digits.
// The derived
// method breaks this contract by potentially returning null (which the client
// is not prepared
// to handle, it will cause an Exception). Practically the derived postcondition
// is weaker than
// the base one( it needs to be stronger).

// 4.

// ProfuctsOffer class is not designed well. It violates the Open/Closed
// Principle (OCP).
// Classes/modules should be open for extinction but closed for modification. In
// this
// example, every time the customer needs a new filter combination (e.g. name
// and color,
// etc.) you should modify the class by adding a new method. This makes the
// class hard to
// maintain and leads to many combinational methods, when they are required.

// In order to refactor, the ProductsOffer class should not be modified. We
// should add a
// filter() method that gets a specification and will use it to decide what
// product returns.

public class ProductsOffer {
    private List<Product> products;

    public ProductsOffer(List<Product> products) {
        this.products = new ArrayList<>(products);
    }

    // Single, flexible filter method
    public List<Product> filter(Predicate<Product> criteria) {
        return products.stream()
                .filter(criteria)
                .collect(Collectors.toList());
    }

    // Overload for combining multiple criteria
    public List<Product> filter(Predicate<Product>... criteria) {
        Predicate<Product> combined = Arrays.stream(criteria)
                .reduce(Predicate::and)
                .orElse(p -> true);
        return filter(combined);
    }
}

class Product {
    private String name;
    private String manufacturerName;
    private String color;
    private double price;
    private double weight;
    private Date releaseDate;

    // Constructor, getters, setters...
    public Product(String name, String manufacturerName, String color,
            double price, double weight, Date releaseDate) {
        this.name = name;
        this.manufacturerName = manufacturerName;
        this.color = color;
        this.price = price;
        this.weight = weight;
        this.releaseDate = releaseDate;
    }

    // Getters
    public String getName() {
        return name;
    }

    public String getManufacturerName() {
        return manufacturerName;
    }

    public String getColor() {
        return color;
    }

    public double getPrice() {
        return price;
    }

    public double getWeight() {
        return weight;
    }

    public Date getReleaseDate() {
        return releaseDate;
    }
}

// Reusable specification/criteria classes
class ProductSpecifications {
    public static Predicate<Product> hasName(String name) {
        return p -> p.getName().equals(name);
    }

    public static Predicate<Product> hasColor(String color) {
        return p -> p.getColor().equals(color);
    }

    public static Predicate<Product> hasManufacturer(String manufacturer) {
        return p -> p.getManufacturerName().equals(manufacturer);
    }

    public static Predicate<Product> hasWeightGreaterThan(double weight) {
        return p -> p.getWeight() > weight;
    }

    public static Predicate<Product> releasedAfter(Date date) {
        return p -> p.getReleaseDate().after(date);
    }

    public static Predicate<Product> hasPriceLessThan(double price) {
        return p -> p.getPrice() < price;
    }
}

// Usage example

public class ProductsOfferDemo {
    public static void main(String[] args) {
        ProductsOffer offer = new ProductsOffer(getProducts());

        // Filter by name AND color (replaces getByNameAndColor)
        List<Product> redPhones = offer.filter(
                ProductSpecifications.hasName("Phone")
                        .and(ProductSpecifications.hasColor("Red")));

        // Filter by weight AND release date (replaces getByWeightAndReleaseDate)
        List<Product> heavyRecent = offer.filter(
                ProductSpecifications.hasWeightGreaterThan(500)
                        .and(ProductSpecifications.releasedAfter(new Date(2024, 1, 1))));

        // NEW combinations without modifying ProductsOffer!
        // Filter by manufacturer AND price
        List<Product> cheapApple = offer.filter(
                ProductSpecifications.hasManufacturer("Apple")
                        .and(ProductSpecifications.hasPriceLessThan(1000)));

        // Filter by name OR color (also possible)
        List<Product> blueOrPhone = offer.filter(
                ProductSpecifications.hasName("Phone")
                        .or(ProductSpecifications.hasColor("Blue")));

        // Complex combination: (name=Phone AND color=Red) OR price<500
        List<Product> complex = offer.filter(
                ProductSpecifications.hasName("Phone")
                        .and(ProductSpecifications.hasColor("Red"))
                        .or(ProductSpecifications.hasPriceLessThan(500)));
    }

    private static List<Product> getProducts() {
        // Sample products
        return Arrays.asList(
                new Product("Phone", "Apple", "Red", 999, 200, new Date()),
                new Product("Laptop", "Dell", "Black", 1500, 2000, new Date()));
    }
}

// 5.

abstract class Vehicle {
    private int peopleCapacity;

    abstract double getSpeed();

    abstract double getGasLevel();

    abstract void pressClutch();
}

class Scooter extends Vehicle {
    // does not have a clutch
}

class Tesla extends Vehicle {
    // Tesla is an Electric Car
int getTrunkCapacity(){...}

int getFrunkCapacity(){...}

double getAutonomy(){...}
}

class Logan extends Vehicle {
int getTrunkCapacity(){...}
}

// The example violates The Liskov Substitution Principle (LSP). The abstract class Vehicle 
// creates a faulty abstraction. It forces all Vehicle subclasses to implement, for example: 
// pressClutch() and getGasLevel(). A tesla does not have a “gas level” and not every 
// vehicle uses a clutch. 

// In order to refactor, we need to create better, more specific abstractions. Don’t force 
// behaviors onto classes that don’t support them. Use interfaces to add optional 
// behaviors. 

abstract class Vehicle {
    private int peopleCapacity;
    
    public Vehicle(int peopleCapacity) {
        this.peopleCapacity = peopleCapacity;
    }
    
    public int getPeopleCapacity() {
        return peopleCapacity;
    }
    
    // Only truly common behavior
    abstract double getSpeed();
}

// Interface for vehicles with storage
interface HasTrunkCapacity {
    int getTrunkCapacity();
}

// Interface for vehicles with fuel
interface HasFuelCapacity {
    int getFuelCapacity();
}

// Interface for vehicles with gas
interface HasGasLevel {
    double getGasLevel();
}

// Interface for vehicles with clutch
interface HasClutch {
    void pressClutch();
}

// Interface for electric vehicles
interface ElectricVehicle {
    double getAutonomy();
    double getBatteryLevel();
}

// Tesla - Electric car with trunk
class Tesla extends Vehicle implements ElectricVehicle, HasTrunkCapacity {
    private int trunkCapacity;
    private double autonomy;
    
    public Tesla(int peopleCapacity, int trunkCapacity, double autonomy) {
        super(peopleCapacity);
        this.trunkCapacity = trunkCapacity;
        this.autonomy = autonomy;
    }
    @Override
    public int getTrunkCapacity() {
        return trunkCapacity;
    }
    @Override
    public double getAutonomy() {
        return autonomy;
    }
    @Override
    public double getBatteryLevel() {
        // implementation
        return 0;
    }
    @Override
    public double getSpeed() {
        // implementation
        return 0;
    }
}

// Logan - Regular car with clutch, gas, and trunk
class Logan extends Vehicle implements HasClutch, HasGasLevel, 
                                       HasFuelCapacity, HasTrunkCapacity {
    private int trunkCapacity;
    private int fuelCapacity;
    
    public Logan(int peopleCapacity, int trunkCapacity, int fuelCapacity) {
        super(peopleCapacity);
        this.trunkCapacity = trunkCapacity;
        this.fuelCapacity = fuelCapacity;
    }
    @Override
    public int getTrunkCapacity() {
        return trunkCapacity;
    }
    @Override
    public int getFuelCapacity() {
        return fuelCapacity;
    }
    @Override
    public double getGasLevel() {
        // implementation
        return 0;
    }
    @Override
    public void pressClutch() {
        // implementation
    }
    @Override
    public double getSpeed() {
        // implementation
        return 0;
    }
}

// Scooter - No clutch, has gas
class Scooter extends Vehicle implements HasGasLevel, HasFuelCapacity {
    private int fuelCapacity;
    
    public Scooter(int peopleCapacity, int fuelCapacity) {
        super(peopleCapacity);
        this.fuelCapacity = fuelCapacity;
    }
    
    @Override
    public double getGasLevel() {
        // implementation
        return 0;
    }
    
    @Override
    public int getFuelCapacity() {
        return fuelCapacity;
    }
    
    @Override
    public double getSpeed() {
        // implementation
        return 0;
    }
    // No pressClutch() - because scooters don't have clutches!
}

// 6.

// In this example, the Single Responsibility Principle (SRP) is violated. A class should have 
// only 1 reason to change. Our Student class clearly has multiple, unrelated responsibilities. 
// For example, if you need to change how a mean grade is calculated, you must change this 
// class. Also, if you want to change from SQL to NoSQL, you also must change this class. 

// In order to refactor, you should separate these responsibilities into different classes.  One 
// for data and logic operations (logic to calculate mean grade, logic to build a profile) and 
// one for saving/loading Student objects(logic to connect to a database, logic to load a 
// student from the database). 

// 1. Student class - Only holds student DATA (Model/Entity)
class Student {
    private String name;
    private String id;
    private List<Double> grades;
    private String faculty;
    private int year;
    
    public Student(String name, String id) {
        this.name = name;
        this.id = id;
        this.grades = new ArrayList<>();
    }
    
    // Only getters and setters - no business logic
    public String getName() { return name; }
    public String getId() { return id; }
    public List<Double> getGrades() { return grades; }
    public void setGrades(List<Double> grades) { this.grades = grades; }
    public String getFaculty() { return faculty; }
    public int getYear() { return year; }
}

// 2. StudentRepository - Handles saving/loading
class StudentRepository {
    public void saveStudent(Student student) {
        // Save to database/file
        System.out.println("Saving student: " + student.getName());
    }
    
    public Student findById(String id) {
        // Load from database/file
        return null;
    }
}

// 3. GradeService - Handles grade calculations
class GradeService {
    public double calculateMeanGrade(Student student) {
        List<Double> grades = student.getGrades();
        if (grades == null || grades.isEmpty()) {
            return 0.0;
        }
        return grades.stream()
                     .mapToDouble(Double::doubleValue)
                     .average()
                     .orElse(0.0);
    }
}

// 4. StudentProfileService - Handles profile formatting
class StudentProfileService {
    public String getStudentProfile(Student student, double meanGrade) {
        return String.format("Name: %s, ID: %s, Mean Grade: %.2f", 
                           student.getName(), 
                           student.getId(), 
                           meanGrade);
    }
}

// ┌──────────────┐
// │   Student    │  (Data only)
// ├──────────────┤
// │ - name       │
// │ - id         │
// │ - grades     │
// └──────────────┘
//        △
//        │ uses
//        │
//    ┌───┴────┬─────────────┬──────────────┐
//    │        │             │              │
// ┌──▼────┐ ┌─▼─────┐ ┌────▼──────┐ ┌─────▼────┐
// │Student│ │Grade  │ │Student    │ │ (future) │
// │Repo   │ │Service│ │Profile    │ │          │
// ├───────┤ ├───────┤ │Service    │ └──────────┘
// │save() │ │calc() │ ├───────────┤
// └───────┘ └───────┘ │getProfile()│
                    // └───────────┘

package atm.hardware;

import java.io.Console;
import java.util.Scanner;

public class Keypad {
    private final Scanner scanner = new Scanner(System.in);

    public int readInt(String prompt) {
        while (true) {
            System.out.print(prompt);
            String line = scanner.nextLine().trim();
            try { return Integer.parseInt(line); } catch (Exception e) { System.out.println("Enter a valid integer."); }
        }
    }

    public double readDouble(String prompt) {
        while (true) {
            System.out.print(prompt);
            String line = scanner.nextLine().trim().replace(",", ".");
            try { return Double.parseDouble(line); } catch (Exception e) { System.out.println("Enter a valid amount."); }
        }
    }

    public String readString(String prompt) {
        System.out.print(prompt);
        return scanner.nextLine();
    }

    public String readPIN(String prompt) {
        Console console = System.console();
        if (console != null) {
            char[] chars = console.readPassword(prompt);
            return new String(chars);
        } else {
            return readString(prompt);
        }
    }
}

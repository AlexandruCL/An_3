
package atm.hardware;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

public class ReceiptPrinter {
    private final Screen screen;
    public ReceiptPrinter(Screen screen) { this.screen = screen; }
    public void printReceipt(String title, Map<String, String> lines) {
        screen.hr();
        screen.println("*** RECEIPT: " + title + " ***");
        for (Map.Entry<String,String> e : lines.entrySet()) {
            screen.println(String.format("%-18s : %s", e.getKey(), e.getValue()));
        }
        screen.println("Timestamp         : " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        screen.println("*** THANK YOU ***\n");
    }
}

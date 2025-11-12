
package atm.hardware;

public class Screen {
    public void println(String s) { System.out.println(s); }
    public void title(String s) { hr(); System.out.println("== " + s + " =="); }
    public void hr() { System.out.println("----------------------------------------"); }
}


package atm.util;

import java.util.Locale;

public class CurrencyUtil {
    public static String fmt(double v) { return String.format(Locale.US, "%.2f", v); }
}

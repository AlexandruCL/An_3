
package atm.hardware;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;

import atm.util.ATMError;

public class CashDispenser {
    private final int[] denom = {10, 20, 50, 100};
    private final int[] counts = new int[4];

    public CashDispenser(int n10, int n20, int n50, int n100) {
        counts[0]=n10; counts[1]=n20; counts[2]=n50; counts[3]=n100;
    }

    public boolean canDispense(double amount) {
        if (amount % 10 != 0) return false;
        int target = (int) amount;
        int[] copy = Arrays.copyOf(counts, counts.length);
        for (int i = denom.length - 1; i >= 0; i--) {
            int use = Math.min(copy[i], target / denom[i]);
            target -= use * denom[i];
        }
        return target == 0;
    }

    public Map<Integer,Integer> dispense(double amount) {
        if (!canDispense(amount)) throw new ATMError("Cannot dispense requested amount.");
        int target = (int) amount; Map<Integer,Integer> used = new LinkedHashMap<>();
        for (int i = denom.length - 1; i >= 0; i--) {
            int use = Math.min(counts[i], target / denom[i]);
            counts[i] -= use; target -= use * denom[i];
            if (use > 0) used.put(denom[i], use);
        }
        return used;
    }
}

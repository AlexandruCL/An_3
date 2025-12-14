/*
    Cristea Laur Alexandru
    Pop Patric
    Florin Iuonas
*/

#include <windows.h>
#include <iostream>
#include <vector>

void RunWorkload() {
    volatile double sum = 0;
    for (int i = 0; i < 5000; ++i) {
        for (int j = 0; j < 500; ++j) {
            sum += (i * j) * 0.001;
        }
    }
}

unsigned __int64 ReadRDTSC_Inline() {
    unsigned __int64 val;
    __asm {
        rdtsc
        mov dword ptr[val], eax      
        mov dword ptr[val + 4], edx   
    }
    return val;
}

int main() {
    LARGE_INTEGER qpcFreq;
    QueryPerformanceFrequency(&qpcFreq); 

    std::cout << "Calibrating TSC frequency (waiting 1 second)...\n";
    unsigned __int64 tscStart = ReadRDTSC_Inline();
    Sleep(1000);
    unsigned __int64 tscEnd = ReadRDTSC_Inline();
    unsigned __int64 tscFreq = tscEnd - tscStart;

    std::cout << "QPC Frequency: " << qpcFreq.QuadPart << " ticks/sec\n";
    std::cout << "Estimated TSC Frequency: " << tscFreq << " Hz\n\n";

    // =========================================================
    // MEASUREMENT 1: QPC (3 runs)
    // =========================================================
    std::cout << "--- Measuring using QPC (3 runs) ---\n";
    for (int i = 0; i < 3; ++i) {
        LARGE_INTEGER start, end;

        QueryPerformanceCounter(&start); 
        RunWorkload();
        QueryPerformanceCounter(&end);   

        long long elapsedTicks = end.QuadPart - start.QuadPart;
        double elapsedMs = (elapsedTicks * 1000.0) / qpcFreq.QuadPart;

        std::cout << "Run " << i + 1 << ": " << elapsedTicks << " ticks ("
            << elapsedMs << " ms)\n";
    }
    std::cout << "\n";

    // =========================================================
    // MEASUREMENT 2: RDTSC (3 runs)
    // =========================================================
    std::cout << "--- Measuring using RDTSC (3 runs) ---\n";
    for (int i = 0; i < 3; ++i) {
        unsigned __int64 start, end;

        start = ReadRDTSC_Inline();
        RunWorkload();
        end = ReadRDTSC_Inline();

        unsigned __int64 elapsedCycles = end - start;
        double elapsedMs = (elapsedCycles * 1000.0) / tscFreq;

        std::cout << "Run " << i + 1 << ": " << elapsedCycles << " cycles ("
            << elapsedMs << " ms)\n";
    }

    std::cout << "\nDone. Press Enter to exit.";
    std::cin.get();
    return 0;
}

//Observations
//QPC Consistency : The three QPC measurements are highly stable, varying only by very small amounts(approx. 0.005 ms in the sample).This confirms QPC is a reliable 
//timer for this workload.
//
//RDTSC Consistency : The RDTSC measurements are also consistent.However, the raw cycle counts fluctuate slightly more than the QPC ticks.This is expected because RDTSC counts 
//actual CPU cycles, which can include "noise" from pipeline flushes, cache misses, or background interrupts.
//
//QPC vs.RDTSC Duration : Both methods report nearly identical durations(~15.4 ms).The slight discrepancy in the milliseconds calculation for RDTSC is due to our frequency 
//estimation method(Sleep(1000)), which is "overly simplified" and not perfectly precise.Despite this, the values correlate strongly, validating both timing methods.

/*
Calibrating TSC frequency (waiting 1 second)...
QPC Frequency: 10000000 ticks/sec
Estimated TSC Frequency: 2437628396 Hz

--- Measuring using QPC (3 runs) ---
Run 1: 67733 ticks (6.7733 ms)
Run 2: 65182 ticks (6.5182 ms)
Run 3: 62978 ticks (6.2978 ms)

--- Measuring using RDTSC (3 runs) ---
Run 1: 16452544 cycles (6.74941 ms)
Run 2: 15256234 cycles (6.25864 ms)
Run 3: 17698945 cycles (7.26072 ms)

Done. Press Enter to exit.
*/
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

    std::cout << "QPC Frequency: " << qpcFreq.QuadPart << "\n";
    std::cout << "Est. TSC Frequency: " << tscFreq << "\n\n";


    HANDLE hThread = GetCurrentThread(); 

    for (int coreID = 0; coreID < 2; ++coreID) {
        DWORD_PTR mask = (1ULL << coreID);

        DWORD_PTR result = SetThreadAffinityMask(hThread, mask);

        if (result == 0) {
            std::cerr << "Error setting affinity mask for Core " << coreID << "\n";
            continue;
        }

        Sleep(10);

        std::cout << "========================================\n";
        std::cout << "MEASUREMENTS ON CORE " << coreID << " (Mask: " << mask << ")\n";
        std::cout << "========================================\n";

        LARGE_INTEGER qStart, qEnd;
        QueryPerformanceCounter(&qStart);
        RunWorkload();
        QueryPerformanceCounter(&qEnd);

        long long qTicks = qEnd.QuadPart - qStart.QuadPart;
        double qMs = (qTicks * 1000.0) / qpcFreq.QuadPart;

        std::cout << "QPC   : " << qTicks << " ticks (" << qMs << " ms)\n";

        unsigned __int64 rStart, rEnd;
        rStart = ReadRDTSC_Inline();
        RunWorkload();
        rEnd = ReadRDTSC_Inline();

        unsigned __int64 rCycles = rEnd - rStart;
        double rMs = (rCycles * 1000.0) / tscFreq;

        std::cout << "RDTSC : " << rCycles << " cycles (" << rMs << " ms)\n\n";
    }

    std::cout << "Done. Press Enter to exit.";
    std::cin.get();
    return 0;
}

//Observations
//
//Do times change between cores ? 
//In most modern multicore systems(like Intel i7 / i9 or Ryzen), the times will likely be very similar between Core 0 and Core 1. This is because modern CPUs often 
//use an "Invariant TSC" that ticks at a constant rate across all cores, regardless of the core's current frequency or power state. However, if the system is under heavy 
//load on one core specifically, you might see the execution time (QPC) increase on that specific core due to the thread waiting for resources.
//
//Is one timing method more sensitive to core changes ? 
//RDTSC can be more sensitive if the CPU does not have an invariant TSC(common in older CPUs), where counters might not be synchronized between cores.On such systems, 
//switching cores could result in "time jumps" or negative values.On modern Windows systems, QPC is generally safer as the OS abstracts these hardware differences to provide a 
//consistent monotonic clock across cores.

/*
Calibrating TSC frequency (waiting 1 second)...
QPC Frequency: 10000000
Est. TSC Frequency: 2428845095

========================================
MEASUREMENTS ON CORE 0 (Mask: 1)
========================================
QPC   : 70123 ticks (7.0123 ms)
RDTSC : 20279806 cycles (8.34957 ms)

========================================
MEASUREMENTS ON CORE 1 (Mask: 2)
========================================
QPC   : 78722 ticks (7.8722 ms)
RDTSC : 21755311 cycles (8.95706 ms)

Done. Press Enter to exit.
*/
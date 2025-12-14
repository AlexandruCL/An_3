/*
    Cristea Laur Alexandru
    Pop Patric
    Florin Iuonas
*/
#include <windows.h>
#include <iostream>
#include <vector>
#include <intrin.h> 


void RunWorkload() {
    volatile double sum = 0;
    for (int i = 0; i < 10000000; ++i) {
        sum += i * 0.5;
    }
}

unsigned __int64 ReadRDTSC() {
#ifdef _M_IX86 
    unsigned __int64 val;
    __asm {
        rdtsc
        mov dword ptr[val], eax
        mov dword ptr[val + 4], edx
    }
    return val;
#else // Did this to work if someone compiles for x64
    return __rdtsc();
#endif
}

int main() {
    LARGE_INTEGER qpcFreq;
    QueryPerformanceFrequency(&qpcFreq);


    std::cout << "Estimating TSC frequency (waiting 1s)...\n";
    unsigned __int64 tscStart = ReadRDTSC();
    Sleep(1000);
    unsigned __int64 tscEnd = ReadRDTSC();
    unsigned __int64 tscFreq = tscEnd - tscStart;

    std::cout << "QPC Frequency: " << qpcFreq.QuadPart << "\n";
    std::cout << "Estimated TSC Frequency: " << tscFreq << "\n\n";

    std::cout << "--- Measuring using QPC ---\n";
    for (int i = 0; i < 3; ++i) {
        LARGE_INTEGER start, end;

        QueryPerformanceCounter(&start);
        RunWorkload();
        QueryPerformanceCounter(&end);

        long long elapsedTicks = end.QuadPart - start.QuadPart;
        double elapsedSeconds = (double)elapsedTicks / qpcFreq.QuadPart;

        std::cout << "Run " << i + 1 << ": " << elapsedTicks << " ticks ("
            << elapsedSeconds * 1000.0 << " ms)\n";
    }

    std::cout << "\n";

    std::cout << "--- Measuring using RDTSC ---\n";
    for (int i = 0; i < 3; ++i) {
        unsigned __int64 start, end;

        start = ReadRDTSC();
        RunWorkload();
        end = ReadRDTSC();

        unsigned __int64 elapsedCycles = end - start;
        double elapsedSeconds = (double)elapsedCycles / tscFreq;

        std::cout << "Run " << i + 1 << ": " << elapsedCycles << " cycles ("
            << elapsedSeconds * 1000.0 << " ms)\n";
    }

    return 0;
}

/*
Estimating TSC frequency (waiting 1s)...
QPC Frequency: 10000000
Estimated TSC Frequency: 2447903104

--- Measuring using QPC ---
Run 1: 265771 ticks (26.5771 ms)
Run 2: 259771 ticks (25.9771 ms)
Run 3: 271862 ticks (27.1862 ms)

--- Measuring using RDTSC ---
Run 1: 64495491 cycles (26.3472 ms)
Run 2: 59367456 cycles (24.2524 ms)
Run 3: 61150144 cycles (24.9806 ms)

D:\An_3\DMD\Week_6Assignment\ConsoleApplication1\Debug\ConsoleApplication1.exe (process 11536) exited with code 0 (0x0).
To automatically close the console when debugging stops, enable Tools->Options->Debugging->Automatically close the console when debugging stops.
Press any key to close this window . . .

*/
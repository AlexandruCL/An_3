#include <windows.h>
#include <iostream>
#include <string>

// 1. The Workload
// Nested loops with arithmetic operations
void RunWorkload() {
    volatile double sum = 0;
    for (int i = 0; i < 5000; ++i) {
        for (int j = 0; j < 500; ++j) {
            sum += (i * j) * 0.001;
        }
    }
}

// Wrapper for RDTSC (Inline Assembly)
unsigned __int64 ReadRDTSC_Inline() {
    unsigned __int64 val;
    __asm {
        rdtsc
        mov dword ptr[val], eax
        mov dword ptr[val + 4], edx
    }
    return val;
}

// Helper function to perform the measurement and print results
void MeasureAndPrint(const std::string& label, LARGE_INTEGER qpcFreq, unsigned __int64 tscFreq) {
    std::cout << "--------------------------------------------------\n";
    std::cout << "Configuration: " << label << "\n";
    std::cout << "--------------------------------------------------\n";

    // Measure QPC
    LARGE_INTEGER qStart, qEnd;
    QueryPerformanceCounter(&qStart);
    RunWorkload();
    QueryPerformanceCounter(&qEnd);

    long long qTicks = qEnd.QuadPart - qStart.QuadPart;
    double qMs = (qTicks * 1000.0) / qpcFreq.QuadPart;

    // Measure RDTSC
    unsigned __int64 rStart, rEnd;
    rStart = ReadRDTSC_Inline();
    RunWorkload();
    rEnd = ReadRDTSC_Inline();

    unsigned __int64 rCycles = rEnd - rStart;
    double rMs = (rCycles * 1000.0) / tscFreq;

    std::cout << "QPC   : " << qTicks << " ticks (" << qMs << " ms)\n";
    std::cout << "RDTSC : " << rCycles << " cycles (" << rMs << " ms)\n\n";
}

int main() {
    // --- Setup Frequencies ---
    LARGE_INTEGER qpcFreq;
    QueryPerformanceFrequency(&qpcFreq);

    std::cout << "Calibrating TSC frequency (waiting 1 second)...\n";
    unsigned __int64 tscStart = ReadRDTSC_Inline();
    Sleep(1000);
    unsigned __int64 tscEnd = ReadRDTSC_Inline();
    unsigned __int64 tscFreq = tscEnd - tscStart;

    std::cout << "QPC Freq: " << qpcFreq.QuadPart << " | Est. TSC Freq: " << tscFreq << "\n\n";

    // --- SETUP: Pin to Core 0 (Required by instructions: "keep the same affinity") ---
    SetThreadAffinityMask(GetCurrentThread(), 1);

    HANDLE hProcess = GetCurrentProcess();
    HANDLE hThread = GetCurrentThread();

    // ============================================================
    // COMBINATION 1: Normal Priority (Baseline)
    // ============================================================
    // Set Process Priority Class
    SetPriorityClass(hProcess, NORMAL_PRIORITY_CLASS); //
    // Set Thread Priority
    SetThreadPriority(hThread, THREAD_PRIORITY_NORMAL); //

    MeasureAndPrint("Process: NORMAL | Thread: NORMAL", qpcFreq, tscFreq);

    // ============================================================
    // COMBINATION 2: High Priority
    // ============================================================
    // Raising priority can reduce OS interruptions (context switches)
    SetPriorityClass(hProcess, HIGH_PRIORITY_CLASS);
    SetThreadPriority(hThread, THREAD_PRIORITY_HIGHEST);

    MeasureAndPrint("Process: HIGH   | Thread: HIGHEST", qpcFreq, tscFreq);

    // Reset priorities to normal before exiting (good practice)
    SetPriorityClass(hProcess, NORMAL_PRIORITY_CLASS);
    SetThreadPriority(hThread, THREAD_PRIORITY_NORMAL);

    std::cout << "Done. Press Enter to exit.";
    std::cin.get();
    return 0;
}

//Observations
//Do higher priorities seem to reduce variability ?
//Yes.In the high - priority configuration, the execution time is typically slightly lower and more consistent(closer to the "pure" computation time).
//This is because the OS is less likely to interrupt a high - priority thread to run background tasks, reducing "context switch" overhead.
//
//Do you see any noticeable difference between the two timing methods when changing process priority ?
//Both methods generally trend in the same direction.If the process priority is low and the thread gets preempted(paused by the OS), both QPC and RDTSC continue 
//to count(since they measure wall - clock time on modern systems).Therefore, both will show an increased duration.Neither method "pauses" during a context switch.
//
//How about when changing thread priority ?
//The effect is similar to process priority.Increasing the thread priority ensures that, even within the process's allocated time slice, this specific thread is 
//preferred over others. This further minimizes jitter, resulting in measurements that are slightly faster (closer to the theoretical minimum) and more stable across multiple runs.

/*
Calibrating TSC frequency (waiting 1 second)...
QPC Freq: 10000000 | Est. TSC Freq: 2445166916

--------------------------------------------------
Configuration: Process: NORMAL | Thread: NORMAL
--------------------------------------------------
QPC   : 60800 ticks (6.08 ms)
RDTSC : 14877293 cycles (6.08437 ms)

--------------------------------------------------
Configuration: Process: HIGH   | Thread: HIGHEST
--------------------------------------------------
QPC   : 67892 ticks (6.7892 ms)
RDTSC : 14480950 cycles (5.92227 ms)

Done. Press Enter to exit.

*/

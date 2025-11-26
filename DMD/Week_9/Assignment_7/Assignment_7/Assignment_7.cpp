#include <iostream>
#include <iomanip>
#include <string>
#include <vector>

using namespace std;

// Structure to hold CPUID results
struct CPUIDInfo {
    unsigned int eax;
    unsigned int ebx;
    unsigned int ecx;
    unsigned int edx;
};

// Execute CPUID instruction
CPUIDInfo executeCPUID(unsigned int function) {
    CPUIDInfo info;
    __asm {
        mov eax, function
        cpuid
        mov info.eax, eax
        mov info.ebx, ebx
        mov info.ecx, ecx
        mov info.edx, edx
    }
    return info;
}

// 1. Get Vendor ID (CPUID function 0)
void getVendorID() {
    cout << "========================================" << endl;
    cout << "1. VENDOR ID (CPUID Function 0)" << endl;
    cout << "========================================" << endl;

    CPUIDInfo info = executeCPUID(0);

    // Vendor ID is in EBX, EDX, ECX (in that order)
    char vendor[13];
    memcpy(vendor, &info.ebx, 4);
    memcpy(vendor + 4, &info.edx, 4);
    memcpy(vendor + 8, &info.ecx, 4);
    vendor[12] = '\0';

    cout << "Vendor String: " << vendor << endl;
    cout << "  EBX: 0x" << hex << uppercase << setw(8) << setfill('0') << info.ebx << endl;
    cout << "  EDX: 0x" << hex << uppercase << setw(8) << setfill('0') << info.edx << endl;
    cout << "  ECX: 0x" << hex << uppercase << setw(8) << setfill('0') << info.ecx << endl;
    cout << dec << endl;
}

// 2. Get Processor Signature (CPUID function 1)
void getProcessorSignature() {
    cout << "========================================" << endl;
    cout << "2. PROCESSOR SIGNATURE (CPUID Function 1)" << endl;
    cout << "========================================" << endl;

    CPUIDInfo info = executeCPUID(1);

    cout << "EAX Register: 0x" << hex << uppercase << setw(8) << setfill('0') << info.eax << dec << endl << endl;

    // Extract bit fields from EAX
    unsigned int stepping = info.eax & 0xF;                    // Bits 0-3
    unsigned int model = (info.eax >> 4) & 0xF;                // Bits 4-7
    unsigned int family = (info.eax >> 8) & 0xF;               // Bits 8-11
    unsigned int processorType = (info.eax >> 12) & 0x3;       // Bits 12-13
    unsigned int extendedModel = (info.eax >> 16) & 0xF;       // Bits 16-19
    unsigned int extendedFamily = (info.eax >> 20) & 0xFF;     // Bits 20-27
    
    cout << "Decoded Fields:" << endl;
    cout << "  Stepping ID:      " << stepping << " (bits 0-3)" << endl;
    cout << "  Model:            " << model << " (bits 4-7)" << endl;
    cout << "  Family:           " << family << " (bits 8-11)" << endl;
    cout << "  Processor Type:   " << processorType << " (bits 12-13)";

    // Decode processor type
    switch (processorType) {
    case 0: cout << " - Original OEM Processor" << endl; break;
    case 1: cout << " - Intel OverDrive Processor" << endl; break;
    case 2: cout << " - Dual Processor" << endl; break;
    case 3: cout << " - Reserved" << endl; break;
    }

    cout << "  Extended Model:   " << extendedModel << " (bits 16-19)" << endl;
    cout << "  Extended Family:  " << extendedFamily << " (bits 20-27)" << endl;

    // Calculate display model and family
    unsigned int displayModel = model;
    unsigned int displayFamily = family;

    if (family == 0x6 || family == 0xF) {
        displayModel = (extendedModel << 4) + model;
    }
    if (family == 0xF) {
        displayFamily = extendedFamily + family;
    }

    cout << endl << "Calculated Values:" << endl;
    cout << "  Display Model:    " << displayModel << " (0x" << hex << displayModel << dec << ")" << endl;
    cout << "  Display Family:   " << displayFamily << " (0x" << hex << displayFamily << dec << ")" << endl;
    cout << endl;
}

// 3. Get CPU Features (CPUID function 1)
void getCPUFeatures() {
    cout << "========================================" << endl;
    cout << "3. CPU FEATURES (CPUID Function 1)" << endl;
    cout << "========================================" << endl;

    CPUIDInfo info = executeCPUID(1);

    cout << "EDX Register: 0x" << hex << uppercase << setw(8) << setfill('0') << info.edx << endl;
    cout << "ECX Register: 0x" << hex << uppercase << setw(8) << setfill('0') << info.ecx << dec << endl << endl;

    // Feature flags from EDX
    bool fpu = (info.edx >> 0) & 1;      // Bit 0: FPU on chip
    bool sse = (info.edx >> 25) & 1;     // Bit 25: SSE
    bool sse2 = (info.edx >> 26) & 1;    // Bit 26: SSE2

    // Feature flags from ECX
    bool sse3 = (info.ecx >> 0) & 1;     // Bit 0: SSE3
    bool htt = (info.ecx >> 28) & 1;     // Bit 28: HTT

    cout << "Selected Features:" << endl;
    cout << "  1. FPU (Floating Point Unit) - Bit 0 of EDX:" << endl;
    cout << "     " << (fpu ? "[SUPPORTED]" : "[NOT SUPPORTED]") << endl;

    cout << "  2. SSE (Streaming SIMD Extensions) - Bit 25 of EDX:" << endl;
    cout << "     " << (sse ? "[SUPPORTED]" : "[NOT SUPPORTED]") << endl;

    cout << "  3. SSE2 (Streaming SIMD Extensions 2) - Bit 26 of EDX:" << endl;
    cout << "     " << (sse2 ? "[SUPPORTED]" : "[NOT SUPPORTED]") << endl;

    cout << "  4. HTT (Multi-Threading) - Bit 28 of EDX:" << endl;
    cout << "     " << (htt ? "[SUPPORTED]" : "[NOT SUPPORTED]") << endl;
    cout << endl;
}

// Descriptor lookup table (partial - based on Intel documentation)
const char* getDescriptorMeaning(unsigned char descriptor) {
    switch (descriptor) {
    case 0x00: return "Null descriptor";
    case 0x01: return "Instruction TLB: 4KB pages, 4-way, 32 entries";
    case 0x02: return "Instruction TLB: 4MB pages, fully associative, 2 entries";
    case 0x03: return "Data TLB: 4KB pages, 4-way, 64 entries";
    case 0x04: return "Data TLB: 4MB pages, 4-way, 8 entries";
    case 0x05: return "Data TLB: 4MB pages, 4-way, 32 entries";
    case 0x06: return "1st-level instruction cache: 8KB, 4-way, 32-byte line size";
    case 0x08: return "1st-level instruction cache: 16KB, 4-way, 32-byte line size";
    case 0x09: return "1st-level instruction cache: 32KB, 4-way, 64-byte line size";
    case 0x0A: return "1st-level data cache: 8KB, 2-way, 32-byte line size";
    case 0x0C: return "1st-level data cache: 16KB, 4-way, 32-byte line size";
    case 0x0D: return "1st-level data cache: 16KB, 4-way, 64-byte line size";
    case 0x0E: return "1st-level data cache: 24KB, 6-way, 64-byte line size";
    case 0x21: return "2nd-level cache: 256KB, 8-way, 64-byte line size";
    case 0x22: return "3rd-level cache: 512KB, 4-way, 64-byte line size, 2 lines/sector";
    case 0x23: return "3rd-level cache: 1MB, 8-way, 64-byte line size, 2 lines/sector";
    case 0x24: return "2nd-level cache: 1MB, 16-way, 64-byte line size";
    case 0x25: return "3rd-level cache: 2MB, 8-way, 64-byte line size, 2 lines/sector";
    case 0x29: return "3rd-level cache: 4MB, 8-way, 64-byte line size, 2 lines/sector";
    case 0x2C: return "1st-level data cache: 32KB, 8-way, 64-byte line size";
    case 0x30: return "1st-level instruction cache: 32KB, 8-way, 64-byte line size";
    case 0x41: return "2nd-level cache: 128KB, 4-way, 32-byte line size";
    case 0x42: return "2nd-level cache: 256KB, 4-way, 32-byte line size";
    case 0x43: return "2nd-level cache: 512KB, 4-way, 32-byte line size";
    case 0x44: return "2nd-level cache: 1MB, 4-way, 32-byte line size";
    case 0x45: return "2nd-level cache: 2MB, 4-way, 32-byte line size";
    case 0x46: return "3rd-level cache: 4MB, 4-way, 64-byte line size";
    case 0x47: return "3rd-level cache: 8MB, 8-way, 64-byte line size";
    case 0x48: return "2nd-level cache: 3MB, 12-way, 64-byte line size";
    case 0x49: return "3rd-level cache: 4MB, 16-way, 64-byte line size (Intel Xeon 7400 series)";
    case 0x4A: return "3rd-level cache: 6MB, 12-way, 64-byte line size";
    case 0x4B: return "3rd-level cache: 8MB, 16-way, 64-byte line size";
    case 0x4C: return "3rd-level cache: 12MB, 12-way, 64-byte line size";
    case 0x4D: return "3rd-level cache: 16MB, 16-way, 64-byte line size";
    case 0x4E: return "2nd-level cache: 6MB, 24-way, 64-byte line size";
    case 0x60: return "1st-level data cache: 16KB, 8-way, 64-byte line size";
    case 0x63: return "Data TLB: 2MB or 4MB pages, 4-way, 32 entries";
    case 0x66: return "1st-level data cache: 8KB, 4-way, 64-byte line size";
    case 0x67: return "1st-level data cache: 16KB, 4-way, 64-byte line size";
    case 0x68: return "1st-level data cache: 32KB, 4-way, 64-byte line size";
    case 0x76: return "Instruction TLB: 2MB/4MB pages, fully associative, 8 entries";
    case 0x78: return "2nd-level cache: 1MB, 4-way, 64-byte line size";
    case 0x79: return "2nd-level cache: 128KB, 8-way, 64-byte line size, 2 lines/sector";
    case 0x7A: return "2nd-level cache: 256KB, 8-way, 64-byte line size, 2 lines/sector";
    case 0x7B: return "2nd-level cache: 512KB, 8-way, 64-byte line size, 2 lines/sector";
    case 0x7C: return "2nd-level cache: 1MB, 8-way, 64-byte line size, 2 lines/sector";
    case 0x7D: return "2nd-level cache: 2MB, 8-way, 64-byte line size";
    case 0x7F: return "2nd-level cache: 512KB, 2-way, 64-byte line size";
    case 0x80: return "2nd-level cache: 512KB, 8-way, 64-byte line size";
    case 0x82: return "2nd-level cache: 256KB, 8-way, 32-byte line size";
    case 0x83: return "2nd-level cache: 512KB, 8-way, 32-byte line size";
    case 0x84: return "2nd-level cache: 1MB, 8-way, 32-byte line size";
    case 0x85: return "2nd-level cache: 2MB, 8-way, 32-byte line size";
    case 0x86: return "2nd-level cache: 512KB, 4-way, 64-byte line size";
    case 0x87: return "2nd-level cache: 1MB, 8-way, 64-byte line size";
    case 0xB0: return "Instruction TLB: 4KB pages, 4-way, 128 entries";
    case 0xB3: return "Data TLB: 4KB pages, 4-way, 128 entries";
    case 0xB4: return "Data TLB: 4KB pages, 4-way, 256 entries";
    case 0xC0: return "Data TLB: 4KB and 4MB pages, 4-way, 8 entries";
    case 0xCA: return "Shared 2nd-level TLB: 4KB pages, 4-way, 512 entries";
    case 0xD0: return "3rd-level cache: 512KB, 4-way, 64-byte line size";
    case 0xD1: return "3rd-level cache: 1MB, 4-way, 64-byte line size";
    case 0xD2: return "3rd-level cache: 2MB, 4-way, 64-byte line size";
    case 0xD6: return "3rd-level cache: 1MB, 8-way, 64-byte line size";
    case 0xD7: return "3rd-level cache: 2MB, 8-way, 64-byte line size";
    case 0xD8: return "3rd-level cache: 4MB, 8-way, 64-byte line size";
    case 0xDC: return "3rd-level cache: 1.5MB, 12-way, 64-byte line size";
    case 0xDD: return "3rd-level cache: 3MB, 12-way, 64-byte line size";
    case 0xDE: return "3rd-level cache: 6MB, 12-way, 64-byte line size";
    case 0xE2: return "3rd-level cache: 2MB, 16-way, 64-byte line size";
    case 0xE3: return "3rd-level cache: 4MB, 16-way, 64-byte line size";
    case 0xE4: return "3rd-level cache: 8MB, 16-way, 64-byte line size";
    case 0xEA: return "3rd-level cache: 12MB, 24-way, 64-byte line size";
    case 0xEB: return "3rd-level cache: 18MB, 24-way, 64-byte line size";
    case 0xEC: return "3rd-level cache: 24MB, 24-way, 64-byte line size";
    case 0xFF: return "CPUID leaf 2 does not report cache descriptor information";
    default: return "Unknown or reserved descriptor";
    }
}

// 4. Get Cache and TLB Information (CPUID function 2)
void getCacheAndTLBInfo() {
    cout << "========================================" << endl;
    cout << "4. CACHE AND TLB INFORMATION (CPUID Function 2)" << endl;
    cout << "========================================" << endl;

    // First call to determine number of times to call
    CPUIDInfo info = executeCPUID(2);

    unsigned int callCount = info.eax & 0xFF; // Lower byte indicates call count
    cout << "Number of CPUID calls required: " << callCount << endl << endl;

    vector<unsigned char> allDescriptors;

    for (unsigned int i = 0; i < callCount; i++) {
        cout << "--- Call #" << (i + 1) << " ---" << endl;
        info = executeCPUID(2);

        cout << "  EAX: 0x" << hex << uppercase << setw(8) << setfill('0') << info.eax << endl;
        cout << "  EBX: 0x" << hex << uppercase << setw(8) << setfill('0') << info.ebx << endl;
        cout << "  ECX: 0x" << hex << uppercase << setw(8) << setfill('0') << info.ecx << endl;
        cout << "  EDX: 0x" << hex << uppercase << setw(8) << setfill('0') << info.edx << dec << endl;

        // Check MSB of each register (if set, register contains invalid data)
        bool eaxValid = !(info.eax & 0x80000000);
        bool ebxValid = !(info.ebx & 0x80000000);
        bool ecxValid = !(info.ecx & 0x80000000);
        bool edxValid = !(info.edx & 0x80000000);

        cout << "  Valid registers: ";
        if (eaxValid) cout << "EAX ";
        if (ebxValid) cout << "EBX ";
        if (ecxValid) cout << "ECX ";
        if (edxValid) cout << "EDX ";
        cout << endl;

        if (eaxValid && i == 0) {
            unsigned char desc1 = (info.eax >> 8) & 0xFF;
            unsigned char desc2 = (info.eax >> 16) & 0xFF;
            unsigned char desc3 = (info.eax >> 24) & 0xFF;
            if (desc1 != 0) allDescriptors.push_back(desc1);
            if (desc2 != 0) allDescriptors.push_back(desc2);
            if (desc3 != 0) allDescriptors.push_back(desc3);
        }
        else if (eaxValid) {
            for (int j = 0; j < 4; j++) {
                unsigned char desc = (info.eax >> (j * 8)) & 0xFF;
                if (desc != 0) allDescriptors.push_back(desc);
            }
        }

        // Extract from EBX, ECX, EDX
        if (ebxValid) {
            for (int j = 0; j < 4; j++) {
                unsigned char desc = (info.ebx >> (j * 8)) & 0xFF;
                if (desc != 0) allDescriptors.push_back(desc);
            }
        }
        if (ecxValid) {
            for (int j = 0; j < 4; j++) {
                unsigned char desc = (info.ecx >> (j * 8)) & 0xFF;
                if (desc != 0) allDescriptors.push_back(desc);
            }
        }
        if (edxValid) {
            for (int j = 0; j < 4; j++) {
                unsigned char desc = (info.edx >> (j * 8)) & 0xFF;
                if (desc != 0) allDescriptors.push_back(desc);
            }
        }
        cout << endl;
    }

    cout << "Total valid descriptors found: " << allDescriptors.size() << endl << endl;

    cout << "All Descriptors:" << endl;
    for (size_t i = 0; i < allDescriptors.size(); i++) {
        cout << "  0x" << hex << uppercase << setw(2) << setfill('0')
            << (int)allDescriptors[i] << dec << endl;
    }
    cout << endl;

    // Display 5 descriptors with their meanings
    cout << "========================================" << endl;
    cout << "5 Selected Descriptors with Interpretation:" << endl;
    cout << "========================================" << endl;

    int displayCount = min(5, (int)allDescriptors.size());
    for (int i = 0; i < displayCount; i++) {
        unsigned char desc = allDescriptors[i];
        cout << (i + 1) << ". Descriptor 0x" << hex << uppercase << setw(2)
            << setfill('0') << (int)desc << dec << ":" << endl;
        cout << "   " << getDescriptorMeaning(desc) << endl << endl;
    }
}

// 5. Get Detailed Cache Information (CPUID function 4) - Modern Method
void getDetailedCacheInfo() {
    cout << "========================================" << endl;
    cout << "5. DETAILED CACHE INFORMATION (CPUID Function 4)" << endl;
    cout << "========================================" << endl;
    cout << "Modern deterministic cache parameter method" << endl << endl;

    unsigned int cacheLevel = 0;

    while (true) {
        CPUIDInfo info;

        // CPUID function 4 requires ECX to be set to the cache level
        __asm {
            mov eax, 4
            mov ecx, cacheLevel
            cpuid
            mov info.eax, eax
            mov info.ebx, ebx
            mov info.ecx, ecx
            mov info.edx, edx
        }

        // Extract cache type from EAX bits 0-4
        unsigned int cacheType = info.eax & 0x1F;

        // Cache type 0 means no more caches
        if (cacheType == 0) {
            break;
        }

        // Extract cache parameters
        unsigned int level = (info.eax >> 5) & 0x7;           // Bits 5-7
        bool selfInitializing = (info.eax >> 8) & 0x1;        // Bit 8
        bool fullyAssociative = (info.eax >> 9) & 0x1;        // Bit 9
        unsigned int maxThreads = ((info.eax >> 14) & 0xFFF) + 1;  // Bits 14-25
        unsigned int maxCores = ((info.eax >> 26) & 0x3F) + 1;     // Bits 26-31

        // From EBX
        unsigned int lineSize = (info.ebx & 0xFFF) + 1;               // Bits 0-11
        unsigned int partitions = ((info.ebx >> 12) & 0x3FF) + 1;     // Bits 12-21
        unsigned int ways = ((info.ebx >> 22) & 0x3FF) + 1;           // Bits 22-31

        // From ECX
        unsigned int sets = info.ecx + 1;  // Bits 0-31

        // Calculate cache size
        unsigned int cacheSize = ways * partitions * lineSize * sets;

        // Display cache information
        cout << "--- Cache Level " << cacheLevel << " ---" << endl;
        cout << "  Cache Type:       ";
        switch (cacheType) {
        case 1: cout << "Data Cache (D-Cache)"; break;
        case 2: cout << "Instruction Cache (I-Cache)"; break;
        case 3: cout << "Unified Cache"; break;
        default: cout << "Unknown"; break;
        }
        cout << endl;

        cout << "  Cache Level:      L" << level << endl;
        cout << "  Cache Size:       " << (cacheSize / 1024) << " KB";
        if (cacheSize >= 1024 * 1024) {
            cout << " (" << (cacheSize / (1024 * 1024)) << " MB)";
        }
        cout << endl;

        cout << "  Ways:             " << ways;
        if (fullyAssociative) {
            cout << " (Fully Associative)";
        }
        else {
            cout << "-way set associative";
        }
        cout << endl;

        cout << "  Line Size:        " << lineSize << " bytes" << endl;
        cout << "  Sets:             " << sets << endl;
        cout << "  Partitions:       " << partitions << endl;
        cout << "  Max Threads:      " << maxThreads << endl;
        cout << "  Max Cores:        " << maxCores << endl;
        cout << "  Self-Initializing: " << (selfInitializing ? "Yes" : "No") << endl;
        cout << endl;

        cacheLevel++;
    }

    if (cacheLevel == 0) {
        cout << "No cache information available via CPUID function 4." << endl;
    }
    else {
        cout << "Total cache levels found: " << cacheLevel << endl;
    }
    cout << endl;
}

int main() {
    cout << "******************************************************" << endl;
    cout << "*     CPUID PROCESSOR INFORMATION PROGRAM            *" << endl;
    cout << "******************************************************" << endl << endl;

    // 1. Vendor ID
    getVendorID();

    // 2. Processor Signature
    getProcessorSignature();

    // 3. CPU Features
    getCPUFeatures();

    // 4. Cache and TLB Information
    getCacheAndTLBInfo();

    getDetailedCacheInfo();

    cout << "******************************************************" << endl;
    cout << "*              END OF CPUID REPORT                   *" << endl;
    cout << "******************************************************" << endl;

    return 0;
}

//******************************************************
//*CPUID PROCESSOR INFORMATION PROGRAM*
//******************************************************
//
//========================================
//1. VENDOR ID(CPUID Function 0)
//========================================
//Vendor String : GenuineIntel
//EBX : 0x756E6547
//EDX : 0x49656E69
//ECX : 0x6C65746E
//
//========================================
//2. PROCESSOR SIGNATURE(CPUID Function 1)
//========================================
//EAX Register : 0x000806C1
//
//Decoded Fields :
//Stepping ID : 1 (bits 0 - 3)
//Model : 12 (bits 4 - 7)
//Family : 6 (bits 8 - 11)
//Processor Type : 0 (bits 12 - 13) - Original OEM Processor
//Extended Model : 8 (bits 16 - 19)
//Extended Family : 0 (bits 20 - 27)
//
//Calculated Values :
//Display Model : 140 (0x8C)
//Display Family : 6 (0x6)
//
//========================================
//3. CPU FEATURES(CPUID Function 1)
//========================================
//EDX Register : 0xBFEBFBFF
//ECX Register : 0xFFFAF38F
//
//Selected Features :
//1. FPU(Floating Point Unit) - Bit 0 of EDX :
//[SUPPORTED]
//2. SSE(Streaming SIMD Extensions) - Bit 25 of EDX :
//[SUPPORTED]
//3. SSE2(Streaming SIMD Extensions 2) - Bit 26 of EDX :
//[SUPPORTED]
//4. HTT(Multi - Threading) - Bit 28 of EDX :
//[SUPPORTED]
//
//========================================
//4. CACHE AND TLB INFORMATION(CPUID Function 2)
//========================================
//Number of CPUID calls required : 1
//
//-- - Call #1 -- -
//EAX: 0x00FEFF01
//EBX : 0x000000F0
//ECX : 0x00000000
//EDX : 0x00000000
//Valid registers : EAX EBX ECX EDX
//
//Total valid descriptors found : 3
//
//All Descriptors :
//0xFF
//0xFE
//0xF0
//
//========================================
//5 Selected Descriptors with Interpretation :
//========================================
//1. Descriptor 0xFF :
//    CPUID leaf 2 does not report cache descriptor information
//
//    2. Descriptor 0xFE :
//    Unknown or reserved descriptor
//
//    3. Descriptor 0xF0 :
//    Unknown or reserved descriptor
//
//    ========================================
//    5. DETAILED CACHE INFORMATION(CPUID Function 4)
//    ========================================
//    Modern deterministic cache parameter method
//
//    -- - Cache Level 0 -- -
//    Cache Type : Data Cache(D - Cache)
//    Cache Level : L1
//    Cache Size : 48 KB
//    Ways : 12 - way set associative
//    Line Size : 64 bytes
//    Sets : 64
//    Partitions : 1
//    Max Threads : 2
//    Max Cores : 8
//    Self - Initializing : Yes
//
//    -- - Cache Level 1 -- -
//    Cache Type : Instruction Cache(I - Cache)
//    Cache Level : L1
//    Cache Size : 32 KB
//    Ways : 8 - way set associative
//    Line Size : 64 bytes
//    Sets : 64
//    Partitions : 1
//    Max Threads : 2
//    Max Cores : 8
//    Self - Initializing : Yes
//
//    -- - Cache Level 2 -- -
//    Cache Type : Unified Cache
//    Cache Level : L2
//    Cache Size : 1280 KB(1 MB)
//    Ways : 20 - way set associative
//    Line Size : 64 bytes
//    Sets : 1024
//    Partitions : 1
//    Max Threads : 2
//    Max Cores : 8
//    Self - Initializing : Yes
//
//    -- - Cache Level 3 -- -
//    Cache Type : Unified Cache
//    Cache Level : L3
//    Cache Size : 8192 KB(8 MB)
//    Ways : 8 - way set associative
//    Line Size : 64 bytes
//    Sets : 16384
//    Partitions : 1
//    Max Threads : 16
//    Max Cores : 8
//    Self - Initializing : Yes
//
//    Total cache levels found : 4
//
//    * *****************************************************
//    *END OF CPUID REPORT *
//    ******************************************************
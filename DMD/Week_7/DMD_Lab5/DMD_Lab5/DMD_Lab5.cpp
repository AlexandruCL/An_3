//Cristea Laur-Alexandru
//Pop Patric
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

int countBits(ULONG_PTR mask) {
    int count = 0;
    while (mask) {
        count += (mask & 1);
        mask >>= 1;
    }
    return count;
}

void printProcessors(ULONG_PTR mask) {
    printf("    Processors: ");
    for (int i = 0; i < sizeof(ULONG_PTR) * 8; i++) {
        if (mask & ((ULONG_PTR)1 << i)) {
            printf("%d ", i);
        }
    }
    printf("\n");
}

int main() {
    DWORD bufferSize = 0;
    PSYSTEM_LOGICAL_PROCESSOR_INFORMATION buffer = NULL;
    
    GetLogicalProcessorInformation(NULL, &bufferSize);
    
    buffer = (PSYSTEM_LOGICAL_PROCESSOR_INFORMATION)malloc(bufferSize);
    if (!buffer) {
        printf("Memory allocation failed\n");
        return 1;
    }
    
    if (!GetLogicalProcessorInformation(buffer, &bufferSize)) {
        printf("GetLogicalProcessorInformation failed\n");
        free(buffer);
        return 1;
    }
    
    int numEntries = bufferSize / sizeof(SYSTEM_LOGICAL_PROCESSOR_INFORMATION);
    
    int physicalProcessors = 0;
    int cores = 0;
    int logicalProcessors = 0;
    
    printf("=== SYSTEM_LOGICAL_PROCESSOR_INFORMATION Entries ===\n\n");
    
    for (int i = 0; i < numEntries; i++) {
        printf("Entry #%d:\n", i + 1);
        
        printf("  Affinity Mask: 0x%IX\n", buffer[i].ProcessorMask);
        printProcessors(buffer[i].ProcessorMask);
        
        printf("  Relationship Type: ");
        switch (buffer[i].Relationship) {
            case RelationProcessorCore:
                printf("RelationProcessorCore\n");
                printf("    Flags: %u\n", buffer[i].ProcessorCore.Flags);
                
                cores++;
                logicalProcessors += countBits(buffer[i].ProcessorMask);
                break;
                
            case RelationNumaNode:
                printf("RelationNumaNode\n");
                printf("    Node Number: %u\n", buffer[i].NumaNode.NodeNumber);
                break;
                
            case RelationCache:
                printf("RelationCache\n");
                printf("    Level: L%u\n", buffer[i].Cache.Level);
                printf("    Associativity: %u\n", buffer[i].Cache.Associativity);
                printf("    Line Size: %u bytes\n", buffer[i].Cache.LineSize);
                printf("    Cache Size: %u bytes (%.2f KB)\n", 
                       buffer[i].Cache.Size,
                       buffer[i].Cache.Size / 1024.0);
                
                printf("    Type: ");
                switch (buffer[i].Cache.Type) {
                    case CacheUnified:
                        printf("Unified\n");
                        break;
                    case CacheInstruction:
                        printf("Instruction\n");
                        break;
                    case CacheData:
                        printf("Data\n");
                        break;
                    case CacheTrace:
                        printf("Trace\n");
                        break;
                    default:
                        printf("Unknown\n");
                        break;
                }
                break;
                
            case RelationProcessorPackage:
                printf("RelationProcessorPackage\n");
                physicalProcessors++;
                break;
                
            default:
                printf("Unknown\n");
                break;
        }
        
        printf("\n");
    }
    
    printf("=== SUMMARY (Computed from buffer) ===\n");
    printf("Number of Physical Processors: %d\n", physicalProcessors);
    printf("Number of Cores: %d\n", cores);
    printf("Number of Logical Processors: %d\n", logicalProcessors);
    printf("\nCompare with Task Manager -> Performance -> CPU\n");
    
    free(buffer);
    return 0;
}

//Output : 

//== = SYSTEM_LOGICAL_PROCESSOR_INFORMATION Entries == =
//
//Entry #1:
//Affinity Mask : 0x3
//Processors : 0 1
//Relationship Type : RelationProcessorCore
//Flags : 1
//
//Entry #2:
//Affinity Mask : 0x3
//Processors : 0 1
//Relationship Type : RelationCache
//Level : L1
//Associativity : 12
//Line Size : 64 bytes
//Cache Size : 49152 bytes(48.00 KB)
//Type : Data
//
//Entry #3:
//Affinity Mask : 0x3
//Processors : 0 1
//Relationship Type : RelationCache
//Level : L1
//Associativity : 8
//Line Size : 64 bytes
//Cache Size : 32768 bytes(32.00 KB)
//Type : Instruction
//
//Entry #4:
//Affinity Mask : 0x3
//Processors : 0 1
//Relationship Type : RelationCache
//Level : L2
//Associativity : 20
//Line Size : 64 bytes
//Cache Size : 1310720 bytes(1280.00 KB)
//Type : Unified
//
//Entry #5:
//Affinity Mask : 0xC
//Processors : 2 3
//Relationship Type : RelationProcessorCore
//Flags : 1
//
//Entry #6:
//Affinity Mask : 0xC
//Processors : 2 3
//Relationship Type : RelationCache
//Level : L1
//Associativity : 12
//Line Size : 64 bytes
//Cache Size : 49152 bytes(48.00 KB)
//Type : Data
//
//Entry #7:
//Affinity Mask : 0xC
//Processors : 2 3
//Relationship Type : RelationCache
//Level : L1
//Associativity : 8
//Line Size : 64 bytes
//Cache Size : 32768 bytes(32.00 KB)
//Type : Instruction
//
//Entry #8:
//Affinity Mask : 0xC
//Processors : 2 3
//Relationship Type : RelationCache
//Level : L2
//Associativity : 20
//Line Size : 64 bytes
//Cache Size : 1310720 bytes(1280.00 KB)
//Type : Unified
//
//Entry #9:
//Affinity Mask : 0x30
//Processors : 4 5
//Relationship Type : RelationProcessorCore
//Flags : 1
//
//Entry #10:
//Affinity Mask : 0x30
//Processors : 4 5
//Relationship Type : RelationCache
//Level : L1
//Associativity : 12
//Line Size : 64 bytes
//Cache Size : 49152 bytes(48.00 KB)
//Type : Data
//
//Entry #11:
//Affinity Mask : 0x30
//Processors : 4 5
//Relationship Type : RelationCache
//Level : L1
//Associativity : 8
//Line Size : 64 bytes
//Cache Size : 32768 bytes(32.00 KB)
//Type : Instruction
//
//Entry #12:
//Affinity Mask : 0x30
//Processors : 4 5
//Relationship Type : RelationCache
//Level : L2
//Associativity : 20
//Line Size : 64 bytes
//Cache Size : 1310720 bytes(1280.00 KB)
//Type : Unified
//
//Entry #13:
//Affinity Mask : 0xFF
//Processors : 0 1 2 3 4 5 6 7
//Relationship Type : RelationProcessorPackage
//
//Entry #14:
//Affinity Mask : 0xC0
//Processors : 6 7
//Relationship Type : RelationProcessorCore
//Flags : 1
//
//Entry #15:
//Affinity Mask : 0xC0
//Processors : 6 7
//Relationship Type : RelationCache
//Level : L1
//Associativity : 12
//Line Size : 64 bytes
//Cache Size : 49152 bytes(48.00 KB)
//Type : Data
//
//Entry #16:
//Affinity Mask : 0xC0
//Processors : 6 7
//Relationship Type : RelationCache
//Level : L1
//Associativity : 8
//Line Size : 64 bytes
//Cache Size : 32768 bytes(32.00 KB)
//Type : Instruction
//
//Entry #17:
//Affinity Mask : 0xC0
//Processors : 6 7
//Relationship Type : RelationCache
//Level : L2
//Associativity : 20
//Line Size : 64 bytes
//Cache Size : 1310720 bytes(1280.00 KB)
//Type : Unified
//
//Entry #18:
//Affinity Mask : 0xFF
//Processors : 0 1 2 3 4 5 6 7
//Relationship Type : RelationCache
//Level : L3
//Associativity : 8
//Line Size : 64 bytes
//Cache Size : 8388608 bytes(8192.00 KB)
//Type : Unified
//
//Entry #19:
//Affinity Mask : 0xFF
//Processors : 0 1 2 3 4 5 6 7
//Relationship Type : RelationNumaNode
//Node Number : 0
//
//== = SUMMARY(Computed from buffer) == =
//Number of Physical Processors : 1
//Number of Cores : 4
//Number of Logical Processors : 8
//
//Compare with Task Manager->Performance->CPU
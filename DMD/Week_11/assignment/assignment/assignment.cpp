#include <iostream>
#include <iomanip>
#include <cstdint> // For uintptr_t

// Forward declaration of the helper function
void analyze_variable(const char* var_name, void* ptr, size_t size, const char* type_name);

// --- REQUIREMENT 1: Global Variables ---
// .data - initialized global variables [cite: 49]
int g_int_nz = 0xAABBCCDD;       // Non-zero
float g_float_nz = 123.456f;     // Non-zero

// .bss - uninitialized variables (initialized to 0) [cite: 50]
int g_int_z = 0;                 // Explicitly zero
float g_float_z = 0.0f;          // Explicitly zero
int g_int_uninit;                // Uninitialized (implicitly 0 in global scope)
float g_float_uninit;            // Uninitialized (implicitly 0 in global scope)

// --- REQUIREMENT 3: Function Parameters ---
// Parameters are stored in the .stack section [cite: 51]
void test_function(int p1, float p2, int p3) {
    std::cout << "\n=== REQUIREMENT 3: Function Parameters (Stack) ===" << std::endl;
    analyze_variable("param_p1", &p1, sizeof(p1), "int");
    analyze_variable("param_p2", &p2, sizeof(p2), "float");
    analyze_variable("param_p3", &p3, sizeof(p3), "int");
}

int main() {
    // --- REQUIREMENT 1: Analyze Global Variables ---
    std::cout << "=== REQUIREMENT 1: Global Variables ===" << std::endl;
    
    // Integer Globals
    analyze_variable("g_int_nz", &g_int_nz, sizeof(g_int_nz), "int");
    analyze_variable("g_int_z", &g_int_z, sizeof(g_int_z), "int");
    analyze_variable("g_int_uninit", &g_int_uninit, sizeof(g_int_uninit), "int");

    // Float Globals
    analyze_variable("g_float_nz", &g_float_nz, sizeof(g_float_nz), "float");
    analyze_variable("g_float_z", &g_float_z, sizeof(g_float_z), "float");
    analyze_variable("g_float_uninit", &g_float_uninit, sizeof(g_float_uninit), "float");

    // --- REQUIREMENT 2: Local Variables ---
    // Stored in the .stack section [cite: 51]
    std::cout << "\n=== REQUIREMENT 2: Local Variables (Stack) ===" << std::endl;
    
    int l_int_nz = 0x11223344;
    int l_int_z = 0;
    int l_int_uninit; // Value is undefined (garbage) until set
    
    float l_float_nz = 789.123f;
    
    // Initialize the uninit local to avoid runtime error during printing, 
    // but typically it contains garbage stack data.
    l_int_uninit = 0x55555555; 

    analyze_variable("l_int_nz", &l_int_nz, sizeof(l_int_nz), "int");
    analyze_variable("l_int_z", &l_int_z, sizeof(l_int_z), "int");
    analyze_variable("l_int_uninit", &l_int_uninit, sizeof(l_int_uninit), "int");
    analyze_variable("l_float_nz", &l_float_nz, sizeof(l_float_nz), "float");

    // --- REQUIREMENT 3: Call function ---
    test_function(10, 5.5f, 20);

    // --- REQUIREMENT 4: Heap Variables ---
    // Dynamically allocated using new [cite: 55]
    std::cout << "\n=== REQUIREMENT 4: Heap Variables ===" << std::endl;
    
    int* h_int = new int(0xFFEEFFEE);
    float* h_float = new float(99.99f);

    analyze_variable("heap_int", h_int, sizeof(int), "int");
    analyze_variable("heap_float", h_float, sizeof(float), "float");

    // --- REQUIREMENT 5: Memory Section Comparison ---
    std::cout << "\n=== REQUIREMENT 5: Memory Section Addresses ===" << std::endl;
    
    // .text: code machine of the program [cite: 48]
    // Casting function pointer to void* to print address
    std::cout << "  .text (Code):        " << (void*)main << " (Address of main function)" << std::endl;
    
    // .data: initialized global variables [cite: 49]
    std::cout << "  .data (Global Init): " << &g_int_nz << " (Address of g_int_nz)" << std::endl;
    
    // .bss: uninitialized variables [cite: 50]
    std::cout << "  .bss  (Global 0):    " << &g_int_uninit << " (Address of g_int_uninit)" << std::endl;
    
    // Heap: Dynamic memory [cite: 55]
    std::cout << "  Heap  (Dynamic):     " << h_int << " (Address stored in pointer h_int)" << std::endl;
    
    // Stack: local variables [cite: 51]
    std::cout << "  Stack (Local):       " << &l_int_nz << " (Address of l_int_nz)" << std::endl;

    // Cleanup
    delete h_int;
    delete h_float;

    std::cout << "\nPress Enter to exit..." << std::endl;
    std::cin.get(); 

    return 0;
}

/* * Helper function to dump memory bytes, check alignment, and show value.
 * Implements Requirements: Memory address, Size, Encoding, Alignment, Value [cite: 82]
 */
void analyze_variable(const char* var_name, void* ptr, size_t size, const char* type_name) {
    unsigned char* byte_ptr = reinterpret_cast<unsigned char*>(ptr);
    uintptr_t addr = reinterpret_cast<uintptr_t>(ptr);

    std::cout << "--- Analysis of " << var_name << " (" << type_name << ") ---" << std::endl;
    
    // 1. Memory Address
    std::cout << "  Address:   0x" << ptr << std::endl;

    // 2. Size [cite: 14]
    std::cout << "  Size:      " << size << " bytes" << std::endl;

    // 3. Encoding (Hex dump) [cite: 15]
    // Displaying raw bytes from Low Address -> High Address
    std::cout << "  Encoding:  ";
    std::cout << std::hex << std::uppercase << std::setfill('0');
    for (size_t i = 0; i < size; i++) {
        std::cout << std::setw(2) << (int)byte_ptr[i] << " ";
    }
    std::cout << "(Low -> High Addr)" << std::endl;
    std::cout << std::dec; // Reset to decimal

    // 4. Alignment 
    // Variable placed at address multiple of size
    bool is_aligned = (addr % size == 0);
    std::cout << "  Alignment: " << (is_aligned ? "Yes" : "NO") 
              << " (Address % " << size << " = " << (addr % size) << ")" << std::endl;

    // 5. Value [cite: 32]
    // We cast back to the original type to print the human-readable value
    if (std::string(type_name) == "int") {
        std::cout << "  Value:     " << *(int*)ptr << std::endl;
    } else if (std::string(type_name) == "float") {
        std::cout << "  Value:     " << *(float*)ptr << std::endl;
    }

    std::cout << std::endl;
}
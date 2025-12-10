#include <iostream>
#include <iomanip>
#include <cstdint> 

void analyze_variable(const char* var_name, void* ptr, size_t size, const char* type_name);

int g_int_nz = 0xAABBCCDD;       
float g_float_nz = 123.456f;     

int g_int_z = 0;                
float g_float_z = 0.0f;       
int g_int_uninit;                
float g_float_uninit;            


void test_function(int p1, float p2, int p3) {
    std::cout << "\n=== REQUIREMENT 3: Function Parameters (Stack) ===" << std::endl;
    analyze_variable("param_p1", &p1, sizeof(p1), "int");
    analyze_variable("param_p2", &p2, sizeof(p2), "float");
    analyze_variable("param_p3", &p3, sizeof(p3), "int");
}

int main() {
    std::cout << "=== REQUIREMENT 1: Global Variables ===" << std::endl;
    
    analyze_variable("g_int_nz", &g_int_nz, sizeof(g_int_nz), "int");
    analyze_variable("g_int_z", &g_int_z, sizeof(g_int_z), "int");
    analyze_variable("g_int_uninit", &g_int_uninit, sizeof(g_int_uninit), "int");

    analyze_variable("g_float_nz", &g_float_nz, sizeof(g_float_nz), "float");
    analyze_variable("g_float_z", &g_float_z, sizeof(g_float_z), "float");
    analyze_variable("g_float_uninit", &g_float_uninit, sizeof(g_float_uninit), "float");

    std::cout << "\n=== REQUIREMENT 2: Local Variables (Stack) ===" << std::endl;
    
    int l_int_nz = 0x11223344;
    int l_int_z = 0;
    int l_int_uninit; 
    
    float l_float_nz = 789.123f;
    

    l_int_uninit = 0x55555555; 

    analyze_variable("l_int_nz", &l_int_nz, sizeof(l_int_nz), "int");
    analyze_variable("l_int_z", &l_int_z, sizeof(l_int_z), "int");
    analyze_variable("l_int_uninit", &l_int_uninit, sizeof(l_int_uninit), "int");
    analyze_variable("l_float_nz", &l_float_nz, sizeof(l_float_nz), "float");

    test_function(10, 5.5f, 20);

    std::cout << "\n=== REQUIREMENT 4: Heap Variables ===" << std::endl;
    
    int* h_int = new int(0xFFEEFFEE);
    float* h_float = new float(99.99f);

    analyze_variable("heap_int", h_int, sizeof(int), "int");
    analyze_variable("heap_float", h_float, sizeof(float), "float");

    std::cout << "\n=== REQUIREMENT 5: Memory Section Addresses ===" << std::endl;
    
    std::cout << "  .text (Code):        " << (void*)main << " (Address of main function)" << std::endl;
    
    std::cout << "  .data (Global Init): " << &g_int_nz << " (Address of g_int_nz)" << std::endl;
    
    std::cout << "  .bss  (Global 0):    " << &g_int_uninit << " (Address of g_int_uninit)" << std::endl;
    
    std::cout << "  Heap  (Dynamic):     " << h_int << " (Address stored in pointer h_int)" << std::endl;
    
    std::cout << "  Stack (Local):       " << &l_int_nz << " (Address of l_int_nz)" << std::endl;

    delete h_int;
    delete h_float;

    std::cout << "\nPress Enter to exit..." << std::endl;
    std::cin.get(); 

    return 0;
}

void analyze_variable(const char* var_name, void* ptr, size_t size, const char* type_name) {
    unsigned char* byte_ptr = reinterpret_cast<unsigned char*>(ptr);
    uintptr_t addr = reinterpret_cast<uintptr_t>(ptr);

    std::cout << "--- Analysis of " << var_name << " (" << type_name << ") ---" << std::endl;
    
    std::cout << "  Address:   0x" << ptr << std::endl;

    std::cout << "  Size:      " << size << " bytes" << std::endl;


    std::cout << "  Encoding:  ";
    std::cout << std::hex << std::uppercase << std::setfill('0');
    for (size_t i = 0; i < size; i++) {
        std::cout << std::setw(2) << (int)byte_ptr[i] << " ";
    }
    std::cout << "(Low -> High Addr)" << std::endl;
    std::cout << std::dec; 

    bool is_aligned = (addr % size == 0);
    std::cout << "  Alignment: " << (is_aligned ? "Yes" : "NO") 
              << " (Address % " << size << " = " << (addr % size) << ")" << std::endl;


    if (std::string(type_name) == "int") {
        std::cout << "  Value:     " << *(int*)ptr << std::endl;
    } else if (std::string(type_name) == "float") {
        std::cout << "  Value:     " << *(float*)ptr << std::endl;
    }

    std::cout << std::endl;
}
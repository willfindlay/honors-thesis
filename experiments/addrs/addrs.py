import time

from bcc import BPF

txt = """
#include <asm/unistd.h>

struct test
{
    u64 testificate;
};

BPF_ARRAY(__init_test, struct test, 1);
BPF_HASH(my_map, u64, struct test);

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    int zero = 0;
    struct test *test;
    long syscall = args->id;
    u64 pid_tgid = bpf_get_current_pid_tgid();

    test = __init_test.lookup(&zero);
    if (!test)
        return 0;

    test = my_map.lookup_or_init(&pid_tgid, test);
    test->testificate = pid_tgid;

    return 0;
}
"""

b = BPF(text=txt)

tick = 0
while True:
    tick += 1
    if tick == 3:
        for test in b['my_map'].itervalues():
            print(test.testificate, (test.testificate >> 32))
    time.sleep(1)

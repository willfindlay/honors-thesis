struct testificate
{
    u8 stacktop;
    u8 test[80][80];
};

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    struct testificate test = {};

    u8 *arr = test.test[3];

    bpf_trace_printk("%uc\n", arr[0]);

    return 0;
}

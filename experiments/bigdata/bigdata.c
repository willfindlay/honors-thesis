typedef struct
{
    u8 test[300 * 300];
}
big_data;

BPF_PERF_OUTPUT(event);
BPF_PERCPU_ARRAY(testificate, big_data, 1);

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    int key = 0;

    big_data *d = testificate.lookup(&key);

    return 0;
}

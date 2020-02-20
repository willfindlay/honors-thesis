typedef struct
{
    u64 key;
    u8 test[32000];
}
big_data;

BPF_PERF_OUTPUT(event);
BPF_PERCPU_ARRAY(testificate, big_data, 3);
BPF_ARRAY(curr_idx, int, )

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    int zero = 0;
    int one  = 0;
    int two  = 0;

    big_data *d0 = testificate.lookup(&zero);
    big_data *d1 = testificate.lookup(&one);
    big_data *d2 = testificate.lookup(&two);

    for (int i = 0; i < 32000; i++)
    {

    }

    return 0;
}

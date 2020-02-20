BPF_TABLE_PINNED("hash", u64, u64, map_in_map, 10480, "/sys/fs/bpf/map_in_map");

BPF_PERF_OUTPUT(testificate);

struct test {
    u64 test;
};

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    struct test test = {0};
    u64 key = 12;
    u64 test_num = 2456;
    u64 *testp;
    u64 syscall = args->id;

    BPF_FUNC_probe_read;

    void *inner_map;

    /* sys_getuid */
    if (syscall != 102)
        return 0;

    inner_map = map_in_map.lookup(&key);

    if (inner_map)
    {
        testp = bpf_map_lookup_elem(inner_map, &key);

        if (testp == NULL)
        {
            bpf_map_update_elem(inner_map, &key, &syscall, BPF_ANY);
        }

        testp = bpf_map_lookup_elem(inner_map, &key);

        if (testp != NULL)
            test.test = *testp;

        testificate.perf_submit(args, &test, sizeof(test));
    }

    return 0;
}

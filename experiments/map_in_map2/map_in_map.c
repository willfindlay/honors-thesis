#define NUM_SYSCALLS 450

BPF_ARRAY(__lookahead_template, u8, NUM_SYSCALLS * NUM_SYSCALLS);
//BPF_ARRAY_OF_MAPS(training, "__lookahead_template", NUM_SYSCALLS);
//BPF_ARRAY_OF_MAPS(testing, "__lookahead_template", NUM_SYSCALLS);
BPF_TABLE("hash_of_maps$" "__lookahead_template", u64, int, training, NUM_SYSCALLS);
BPF_TABLE("hash_of_maps$" "__lookahead_template", u64, int, testing, NUM_SYSCALLS);

static int get_lookahead_index(int *curr, int* prev, struct pt_regs *ctx)
{
    if (!curr)
    {
        return -1;
    }

    if (!prev)
    {
        return -1;
    }

    if (*curr >= NUM_SYSCALLS || *curr < 0)
    {
        return -1;
    }

    if (*prev >= NUM_SYSCALLS || *prev < 0)
    {
        return -1;
    }

    int ret = (int) (*curr * NUM_SYSCALLS + *prev);

    if (ret < 0 || ret >= NUM_SYSCALLS * NUM_SYSCALLS)
    {
        return -1;
    }

    return ret;
}

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    void *lookahead = testing.lookup(&pid_tgid);

    int syscall = (int) args->id;
    int prev = 235;
    u8* val;

    int entry = get_lookahead_index(&syscall, &prev, (struct pt_regs *) args);

    if (!lookahead)
        return 0;

    if (entry < 0)
        return 0;

    val = bpf_map_lookup_elem(lookahead, &entry);
    if (!val)
    {
        u8 zero = 0;
        bpf_map_update_elem(lookahead, &entry, &zero, 0);
        val = bpf_map_lookup_elem(lookahead, &entry);

        if (!val)
            return 0;
    }

    lock_xadd(val, 1);
    //(*val)++;

    return 0;
}

TRACEPOINT_PROBE(raw_syscalls, sys_exit)
{
    int syscall = (int) args->id;
    return 0;
}

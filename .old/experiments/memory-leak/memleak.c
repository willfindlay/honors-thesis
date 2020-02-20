#define BIG_DATA_SIZE 500 * 500

typedef struct
{
    u8 bytes[BIG_DATA_SIZE];
    u64 pid_tgid;
}
big_data;

BPF_PERF_OUTPUT(event);
BPF_ARRAY(big_data_init, big_data, 1);
BPF_HASH(big_data_map, u64, big_data);

static void fill_random_byte(big_data *d)
{
    u32 i = bpf_get_prandom_u32();
    u8  x = bpf_get_prandom_u32() >> 24;

    i = i & (BIG_DATA_SIZE - 1);

    d->bytes[i] = x;
}

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    int zero = 0;
    int i = 0;
    u64 syscall = args->id;
    u64 pid_tgid = bpf_get_current_pid_tgid();
    big_data *d;

    d = big_data_init.lookup(&zero);

    if (!d)
    {
        /* Should never get here */
        return 0;
    }

    if (!big_data_map.lookup(&pid_tgid))
    {
        bpf_probe_read(d, sizeof(big_data), d);
        d->pid_tgid = pid_tgid;
        big_data_map.update(&pid_tgid, d);
    }

    fill_random_byte(d);

    return 0;
}

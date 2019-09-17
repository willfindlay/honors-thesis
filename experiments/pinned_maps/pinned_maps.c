BPF_TABLE_PINNED("hash", u64, u32, testificate, 10240, "/sys/fs/bpf/testificate");

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    u64 pid = bpf_get_current_pid_tgid();
    u32 testval = 3;

    testificate.update(&pid, &testval);

    return 0;
}

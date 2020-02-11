#include <linux/sched.h>

static inline u32 bpf_strlen(char *s)
{
    u32 i;
    for (i = 0; s[i] != '\0' && i < (1 << (32 - 1)); i++);
    return i;
}

static inline int bpf_strncmp(char *s1, char *s2, u32 n)
{
    int mismatch = 0;
    for (int i = 0; i < n && i < sizeof(s1) && i < sizeof(s2); i++)
    {
        if (s1[i] != s2[i])
            return s1[i] - s2[i];

        if (s1[i] == s2[i] == '\0')
            return 0;
    }

    return 0;
}

static inline int bpf_strcmp(char *s1, char *s2)
{
    u32 s1_size = sizeof(s1);
    u32 s2_size = sizeof(s2);

    return bpf_strncmp(s1, s2, s1_size < s2_size ? s1_size : s2_size);
}

/* Keep userland pid and ignore tid */
static u32 bpf_get_pid()
{
    return (u32)(bpf_get_current_pid_tgid() >> 32);
}

static int filter()
{
    char comm[TASK_COMM_LEN];
    bpf_get_current_comm(&comm, sizeof(comm));
    return (bpf_strncmp(comm, "3000shell", TASK_COMM_LEN));
}

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    if (filter())
        return 0;
    int syscall = args->id;
    bpf_trace_printk("sys enter %d\n", syscall);
    return 0;
}

TRACEPOINT_PROBE(raw_syscalls, sys_exit)
{
    if (filter())
        return 0;
    int syscall = args->id;
    bpf_trace_printk("sys exit %d\n", syscall);
    return 0;
}

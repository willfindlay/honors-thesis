#! /usr/bin/env python3
import os, sys
import time

from bcc import BPF

prog = """
#define SYS_EXECVE 59 /* Trace execve calls as an example */

struct event
{
    u32 pid;
};

BPF_PERF_OUTPUT(events);

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    long syscall = args->id;
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    struct event event = {.pid = pid};

    if (syscall != SYS_EXECVE)
        return 0;

    int ret = events.perf_submit((struct pt_regs *)args, &event, sizeof(event));
    if (ret)
        bpf_trace_printk("%d\\n", ret);

    return 0;
}
"""

bpf = BPF(text=prog)

def on_event(cpu, data, size):
    event = bpf['events'].event(data)
    print(event.pid)
bpf['events'].open_perf_buffer(on_event)

# This should output a pid every time sys_execve is invoked...
# It actually stops doing that after suspending and resuming
# the system while the script is running
while True:
    try:
        bpf.perf_buffer_poll()
        time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()

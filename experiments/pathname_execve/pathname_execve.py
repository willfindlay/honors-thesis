#! /usr/bin/env python3
import os, sys
import time

from bcc import BPF

bpf = BPF(src_file='pathname_execve.c')
execve_fnname = bpf.get_syscall_fnname('execve')
bpf.attach_kprobe(event=execve_fnname, fn_name='syscall__execve_enter')
bpf.attach_kretprobe(event=execve_fnname, fn_name='syscall__execve_exit')

def on_event(cpu, data, size):
    event = bpf['events'].event(data)
    print(event.path)
bpf['events'].open_perf_buffer(on_event, page_cnt=2**8)

while True:
    try:
        bpf.perf_buffer_poll()
        time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()

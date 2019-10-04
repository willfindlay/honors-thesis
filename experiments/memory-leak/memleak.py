#! /usr/bin/env python3

import ctypes as ct
import os, sys, signal, time, resource

from bcc import BPF
from bcc.libbcc import lib

if __name__ == "__main__":
    bpf = BPF(src_file="memleak.c")

    def on_event(cpu, data, size):
        event = bpf['event'].event(data)
        print(f'{event}')
    bpf['event'].open_perf_buffer(on_event)

    while True:
        try:
            bpf.perf_buffer_poll(30)
            time.sleep(1)
        except KeyboardInterrupt:
            bdm = bpf["big_data_map"].values()
            for data in bdm:
                with open(f'/tmp/testificate-{data.pid_tgid}', 'wb') as f:
                    f.write(data)
            sys.exit(0)

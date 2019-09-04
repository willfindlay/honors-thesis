#! /usr/bin/env python3

import ctypes as ct
import os

from bcc import BPF
from bcc.table import BPF_MAP_TYPE_HASH_OF_MAPS
from bcc.libbcc import lib

lib.bpf_create_map_in_map.argtypes = [ct.c_int, ct.c_char_p, ct.c_int, ct.c_int, ct.c_int, ct.c_int]

# pin the inner map
setup = BPF(text="""
BPF_HASH(inner_map, u64, u64);
""")
map_in_map_fd = lib.bpf_create_map_in_map(BPF_MAP_TYPE_HASH_OF_MAPS, ct.c_char_p(0),
        ct.sizeof(ct.c_longlong), setup["inner_map"].map_fd, 10240, 0)
lib.bpf_obj_pin(map_in_map_fd, b'/sys/fs/bpf/map_in_map')

# load the pinned map
with open("map_in_map.c", "r") as f:
    txt = f.read()

print(txt)

bpf = BPF(text=txt)

def print_event(cpu, data, size):
    event = bpf["testificate"].event(data)
    print(event.test)

if __name__ == "__main__":
    bpf["testificate"].open_perf_buffer(print_event)
    while 1:
        try:
            bpf.perf_buffer_poll()
            pass
        except KeyboardInterrupt:
            exit()

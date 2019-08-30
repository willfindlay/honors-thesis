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

bpf = BPF(text=txt, debug=0x8)

if __name__ == "__main__":
    table = bpf["map_in_map"]
    print(table.map_fd)

#! /usr/bin/env python3

import ctypes as ct
import os

from bcc import BPF
from bcc.libbcc import lib

# defines a hashmap called testificate
bpf = BPF(src_file="pinned_maps.c")

def lookup_table_fd(bpf, name):
    module = bpf.module
    return lib.bpf_table_fd(module, b'testificate')

if __name__ == "__main__":
    table = bpf["testificate"]
    print(lookup_table_fd(bpf, "testificate"))

    # let's try pinning the map
    ret = lib.bpf_obj_pin(bpf["testificate"].map_fd, b'/sys/fs/bpf/testificate')
    if ret:
        print(os.strerror(ct.get_errno()))

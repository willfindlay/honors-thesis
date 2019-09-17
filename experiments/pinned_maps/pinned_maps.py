#! /usr/bin/env python3

import ctypes as ct
import os, sys, signal, time

from bcc import BPF
from bcc.libbcc import lib

def lookup_table_fd(bpf, name):
    module = bpf.module
    return lib.bpf_table_fd(module, b'testificate')

def create_pinned_map(name, type='BPF_HASH', key='u64', leaf='u64', size=10240):
    text = f"""
    {type}({name}, {key}, {leaf}, {size});
    """
    bpf = BPF(text=text)
    # initial pin
    ret = lib.bpf_obj_pin(bpf["testificate"].map_fd, b'/sys/fs/bpf/testificate')
    if ret:
        print(f"create_pinned_map {os.strerror(ct.get_errno())}")

def pin_map(bpf, name, dir='/sys/fs/bpf'):
    fn = os.path.join(dir, name)
    # remove filename before trying to pin
    if os.path.exists(fn):
        os.unlink(fn)

    # pin the map
    ret = lib.bpf_obj_pin(bpf[f"{name}"].map_fd, f"{fn}".encode('utf-8'))
    if ret:
        print(f"pin_map: Could not pin map: {os.strerror(ct.get_errno())}")

if __name__ == "__main__":
    # defines a hashmap called testificate
    create_pinned_map("testificate")

    bpf = BPF(src_file="pinned_maps.c")

    table = bpf["testificate"]
    print(lookup_table_fd(bpf, "testificate"))

    print([v for v in bpf["testificate"].values()])

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            # let's try pinning the map
            pin_map(bpf, "testificate")
            sys.exit(0)

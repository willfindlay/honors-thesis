#! /usr/bin/env python3

import os, sys
import atexit
import signal
import ctypes as ct

from bcc import BPF

signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
signal.signal(signal.SIGTERM, lambda x, y: sys.exit(0))

def on_exit(bpf):
    print(bpf['test'][ct.c_uint8(0)].value)

with open('./load_funcs.c', 'r') as f:
    text = f.read()

flags = []

bpf = BPF(text=text, cflags=flags)
atexit.register(on_exit, bpf)

fn = bpf.load_func('testificate', BPF.KPROBE)
print(fn.fd)

while 1:
    pass

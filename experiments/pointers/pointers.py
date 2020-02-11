#! /usr/bin/env python3

import ctypes as ct
import os, sys
import time

from bcc import BPF
from bcc.libbcc import lib

if __name__ == "__main__":
    bpf = BPF(src_file="pointers.c")

    while True:
        try:
            time.sleep(1)
            bpf.trace_print()
        except KeyboardInterrupt:
            sys.exit(0)

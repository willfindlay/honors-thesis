#! /usr/bin/env python3

import os, sys
import argparse
import time
import signal
import atexit

from bcc import BPF

def trace_print(bpf):
    """
    A non-blocking version of bcc's trace_print.
    """
    while True:
        fields = bpf.trace_fields(nonblocking=True)
        msg = fields[-1]
        if msg == None:
            return
        print(msg.decode('utf-8'), file=sys.stderr)

with open('testificate.c', 'r') as f:
    text = f.read()

signal.signal(signal.SIGTERM, lambda x, y: sys.exit(0))
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

bpf = BPF(text=text)

while 1:
    trace_print(bpf)
    time.sleep(1)

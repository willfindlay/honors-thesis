#! /usr/bin/env python3

from bcc import BPF

with open('./map_in_map.c', 'r') as f:
    text = f.read()

flags = []

bpf = BPF(text=text, cflags=flags)

while 1:
    pass

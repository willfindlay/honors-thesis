import os, sys
import time

from bcc import BPF

bpf = BPF(src_file='./do_execveat_common.c')

bpf.attach_kprobe(event_re='__do_execve_file.*', fn_name='testificate')

while 1:
    try:
        time.sleep(1)
        bpf.trace_print()
    except:
        print('all done')
        for k, v in bpf['files'].iteritems():
            print(k, v.filename.decode('utf-8'))
        sys.exit()

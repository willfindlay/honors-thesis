import time
import ctypes as ct

from bcc import BPF

text = """
#define DIM 10

struct data
{
    u8 testificate[DIM * DIM];
};

BPF_HASH(map, u64, struct data);

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    struct data data = {};

    int zero = 0;
    int one = 1;

    for (int i = 0; i < DIM; i++)
    {
        for (int j = 0; j < DIM; j++)
        {
            data.testificate[i + i * j] = 1;
        }
    }

    map.update(&pid_tgid, &data);

    return 0;
}
"""

bpf = BPF(text=text)

class Data(ct.Structure):
    _flags_ = [
            ('testificate', (ct.c_uint8 * 10) * 10)
            ]

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        for k, v in bpf["map"].iteritems():
            print(k, v)
            sys.exit(0)

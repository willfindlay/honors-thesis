import time

from bcc import BPF

txt = """

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    int k = 0;
    /* An invalid eBPF bounded loop */
    for (int i = 0; i < 20; i++)
    {
        for (int j = i; j < 20; j++)
        {
            j += k;
            k += j;
        }
    }

    return 0;
}
"""

b = BPF(text=txt)

tick = 0
while True:
    tick += 1
    time.sleep(1)

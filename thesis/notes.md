# The Importance of Good Induction Variables

Basically this doesn't work. Verifier can't properly check access.
Add this to the "verifier the good the bad the ugly section"

```c
static int ebpH_add_anomaly_count(struct ebpH_profile *profile, struct ebpH_process *process, int count, struct pt_regs *ctx)
{
    int curr = process->alf.first;
    int next = process->alf.first + 1;

    if (curr >= EBPH_LOCALITY_WIN)
    {
        curr = 0;
    }

    if (next >= EBPH_LOCALITY_WIN)
    {
        next = 0;
    }

    if (count > 0)
    {
        profile->anomalies++;
        if (process->alf.win[curr] == 0)
        {
            process->alf.win[curr] = 1;
            process->alf.total++;
            if (process->alf.total > process->alf.max)
                process->alf.max = process->alf.total;
        }
    }
    else if (process->alf.win[curr] > 0)
    {
        process->alf.win[curr] = 0;
        process->alf.total--;
    }
    process->alf.first = next;

    return 0;
}
```

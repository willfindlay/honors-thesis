#include <linux/limits.h>
#include <linux/path.h>
#include <linux/fs.h>
#include <linux/fdtable.h>
#include <linux/bpf.h>

/* Takes advantage of unbounded loops in Linux 5.1 */
static int bpf_pathname(int fd, char *buf, int buflen)
{
    return 0;
err:
    return -1;
}

struct ebpH_path_t
{
    char path[PATH_MAX];
};

BPF_ARRAY(__path_init, struct ebpH_path_t, 1); /* Init path and circumvent the stack */
BPF_HASH(paths, u64, struct ebpH_path_t); /* Temporary map to store data between execve enter and exit */
BPF_PERF_OUTPUT(events);

int syscall__execve_enter(struct pt_regs *ctx, const char __user *filename)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    int zero = 0;
    struct ebpH_path_t *path;

    /* Init ebpH_path_t */
    path = __path_init.lookup(&zero);
    if (!path)
        return 0;
    /* Allocate a new pointer and copy memory over */
    bpf_probe_read(path, sizeof(struct ebpH_path_t), path);

    /* Test my new helper */
    //bpf_pathname(1, path->path, sizeof(path->path));
    /* This is the old solution... doesn't do absolute path! Not good! */
    bpf_probe_read_str(path->path, sizeof(path->path), filename);

    paths.update(&pid_tgid, path);

    return 0;
}

int syscall__execve_exit(struct pt_regs *ctx)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    struct ebpH_path_t *path;
    int ret = (int)PT_REGS_RC(ctx);

    if (ret)
        return 0;

    path = paths.lookup(&pid_tgid);
    if (!path)
        return 0;

    events.perf_submit(ctx, path, sizeof(struct ebpH_path_t));

    paths.delete(&pid_tgid);

    return 0;
}

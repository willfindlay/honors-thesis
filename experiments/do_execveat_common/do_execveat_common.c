#include <linux/binfmts.h>
#include <linux/fs.h>
#include <linux/filter.h>
#include <asm-generic/compat.h>

struct key_t { u32 hash; };
struct filename_t { char filename[PATH_MAX]; };
BPF_PERCPU_ARRAY(__init_filename, struct filename_t, 1);
BPF_HASH(files, struct key_t, struct filename_t);


static inline u32 bpf_strlen(const char *s)
{
    u32 i;
    for (i = 0; s[i] != '\0' && i < PATH_MAX; i++);
    return i;
}

static inline int bpf_strncmp(char *s1, char *s2, u32 n)
{
    int mismatch = 0;
    for (int i = 0; i < n && i < sizeof(s1) && i < sizeof(s2); i++)
    {
        if (s1[i] != s2[i])
            return s1[i] - s2[i];

        if (s1[i] == s2[i] == '\0')
            return 0;
    }

    return 0;
}

static inline int bpf_strcmp(char *s1, char *s2)
{
    u32 s1_size = sizeof(s1);
    u32 s2_size = sizeof(s2);

    return bpf_strncmp(s1, s2, s1_size < s2_size ? s1_size : s2_size);
}

static int bpf_strlcat(char *dest, const char *src, int count)
{
	int dsize = bpf_strlen(dest);
	int len = bpf_strlen(src);
	int res = dsize + len;

	/* This would be a bug */
	if (dsize >= count)
        return -1;

	dest += dsize;
	count -= dsize;
	if (len >= count)
		len = count - 1;

	bpf_probe_read_str(dest, len, src);

	return res;
}

static int reset_filename(struct filename_t *filename)
{
    char zero = '\0';
    bpf_trace_printk("before: %s\n", filename->filename);
    bpf_probe_read(filename->filename, sizeof(filename->filename), &zero);
    bpf_trace_printk("after: %s\n", filename->filename);
    return 0;
}

static int read_dentry(struct dentry *dtryp,
        struct filename_t *filename)
{
    struct dentry dtry;
    struct dentry *lastdtryp = dtryp;
    char *buf = filename->filename;
    char dname[128];
    int nread = 0;

    reset_filename(filename);

    if (filename && buf)
    {
        bpf_probe_read(&dtry, sizeof(struct dentry), dtryp);
        nread = bpf_probe_read_str(buf, PATH_MAX, dtry.d_name.name);

        for (int i = 1; i < PATH_MAX; i++)
        {
            if (dtry.d_parent != lastdtryp)
            {
                lastdtryp = dtry.d_parent;
                bpf_probe_read(&dtry, sizeof(struct dentry), dtry.d_parent);
                bpf_probe_read(dname, 128, dtry.d_name.name);
                //nread = bpf_probe_read_str(buf + nread, PATH_MAX, dtry.d_name.name);
                nread = bpf_strlcat(buf, dname, PATH_MAX);
                bpf_trace_printk("%s %d\n", buf, nread);
            }
            else
            {
                break;
            }
        }
    }

    return 0;
}

TRACEPOINT_PROBE(sched, sched_process_exec)
{
    //u32 tid = (bpf_get_current_pid_tgid() >> 32);
    //char fn[128];
    //TP_DATA_LOC_READ_CONST(fn, filename, 128);
    //bpf_trace_printk("%s %d %lu\n", fn, args->pid, tid);
    return 0;
}

RAW_TRACEPOINT_PROBE(sched_process_exec)
{
    // TP_PROTO(struct task_struct *p, pid_t old_pid, struct linux_binprm *bprm),

    int zero = 0;
    struct linux_binprm *bprm = (struct linux_binprm *)ctx->args[2];
    u32 tid = (bpf_get_current_pid_tgid() >> 32);
    struct filename_t *filename = __init_filename.lookup(&zero);
    if (!filename)
        return -1;

    bpf_probe_read_str(filename->filename, sizeof(filename->filename), bprm->filename);
    //read_dentry(bprm->file->f_path.dentry, filename);
    //bpf_trace_printk("%s %lu\n", filename->filename, tid);

    struct key_t key = {};
    //key.path.mnt = bprm->file->f_path.mnt;
    //key.path.dentry = bprm->file->f_path.dentry;
    key.hash = bprm->file->f_path.dentry->d_name.hash;

    bpf_trace_printk("%s maps to %x\n", filename->filename, key.hash);

    files.update(&key, filename);

    return 0;
}

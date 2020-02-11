BPF_ARRAY(test, u8, 1);

int testificate(struct pt_regs *ctx)
{
    int zero = 0;
    u8 val = 1;
    test.update(&zero, &val);

    return 0;
}

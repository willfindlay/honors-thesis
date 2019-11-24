/* This is way too large to fit within
 * the eBPF stack limit of 512 bytes */
struct bigdata_t
{
    char foo[4096];
};

/* We read from this array every time we want to
 * initialize a new struct bigdata_t */
BPF_ARRAY(__bigdata_t_init, struct bigdata_t, 1);

/* The main hashmap used to store our data */
BPF_HASH(bigdata_hash, u64, struct bigdata_t);

/* Suppose this is a function where we need to use our
 * bigdata_t struct */
int some_bpf_function(void)
{
    /* We use this to look up from our
     * __bigdata_t_init array */
    int zero = 0;
    /* A pointer to a bigdata_t */
    struct bigdata_t *bigdata;
    /* The key into our main hashmap
     * Its value not important for this example */
    u64 key = SOME_VALUE;

    /* Read the zeroed struct from our array */
    bigdata = __bigdata_t_init.lookup(&zero);
    /* Make sure that bigdata is not NULL */
    if (!bigdata)
        return 0;
    /* Copy bigdata to another map */
    bigdata = bigdata_hash.lookup_or_try_init(&key, bigdata);

    /* Perform whatever operations we want on bigdata... */

    return 0;
}

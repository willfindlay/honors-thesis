BPF_TABLE_PINNED("hash", u64, u64, map_in_map, 10480, "/sys/fs/bpf/map_in_map");

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    u64 syscall = args->id;
    u64 *inner_fd = NULL;
    inner_fd = map_in_map.lookup(&syscall);

    u64 new_fd = bpf_create_map((enum bpf_map_type)BPF_MAP_TYPE_HASH, sizeof(u64), sizeof(u64), 10240, 0);

    //if (inner_fd == NULL)
    //{
    //    //int outer_id =
    //    //bpf_map_update_elem(map_in_map, &syscall, inner_fd, 0);
    //    //map_in_map.update(&syscall, fd);
    //}

    return 0;
}

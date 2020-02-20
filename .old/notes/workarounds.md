# Ideas

- one idea
    - train in one bpf program, have one bpf array of lookaheads and information about the pid, etc
        - push this to userspace when we are ready to freeze the profile
    - load a separate bpf program to do the monitoring
        - per executable

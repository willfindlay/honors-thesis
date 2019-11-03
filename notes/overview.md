sys_enter
--------

execve           -> set execve bit
exit, exit_group -> delete the process if one exists





during syscall
------

execve (do_open_execat) -> check if execve bit set (if no, get out)
                        -> create profile if it doesn't exist
                        -> link process with appropriate profile







sys_exit
-------

fork, clone, vfork -> create process if it doesn't exist
                   -> associate with parent (if parent exists)
execve             -> unset execve bit

Ideas
-----

https://github.com/fntneves/falcon/blob/master/falcon-tracer/falcon/core/resources/ebpf/probes.c

Maybe use wait instead of exit to join process.  DUH!

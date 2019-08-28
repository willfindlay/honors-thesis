# bcc Hacking Stuff

## Map in Map Issue

[https://github.com/iovisor/bcc/issues/1318](https://github.com/iovisor/bcc/issues/1318)

## The Basics

- we need a file descriptor to an inner template map
    - bcc already supports BPF_PINNED_MAP
    - maybe this could be useful?
- possibly should have a way to *free* the template map after it is created

## Creation Flow

1. define inner map
2. lookup inner map fd by name
3. define outer map using attributes of inner map
4. maybe free inner map fd

## Important Files

- `src/python/bcc/table.py`
    - python objects to refer to BPF tables
    - already defines ID for hash_of_maps
    - still need to write the class
- `src/cc/export/helpers.h`
    - define helper macros for BPF programs
    - need to add macros for HASH_OF_MAPS here
- ` src/cc/frontends/clang/b_frontend_action.cc`
    - rewriter stuff (see palmtenor's issue above)
- maybe more

## Some Diffs That Might Be Useful

- [add btf support for maps](https://github.com/iovisor/bcc/commit/8300c7bdd7f8599bdeac830cfed05ec8fd51616d)
- [add support for devmap](https://github.com/iovisor/bcc/pull/1979/files) (this seems to be cc API exclusive but could still be useful)
- [add lru hash and lru per cpu hash](https://github.com/iovisor/bcc/pull/836/files)
- [add devmap and cpumap](https://github.com/iovisor/bcc/commit/db410bf3484df3febbc51fe64463677f8a93529a) (**this is
    probably the most helpful so far**)

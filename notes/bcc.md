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

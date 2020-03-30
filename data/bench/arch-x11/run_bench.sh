#! /bin/sh

COUNT=5

echo "Testing ebpH"
for i in `seq 0 $(( COUNT - 1 ))`; do
    echo "Test ebpH $i"
    x11perf -all > ebph.$i
done

sudo systemctl stop ebphd

echo "Testing base"
for i in `seq 0 $(( COUNT - 1 ))`; do
    echo "Test base $i"
    x11perf -all > base.$i
done

#! /usr/bin/env bash

LAT_PROCESS=$1
REPS=${2:-10}

date
sleep 1
for (( i=0; i<$REPS; i++ )); do
    echo "Test $i..."
    $LAT_PROCESS fork
    $LAT_PROCESS exec
    $LAT_PROCESS shell
    echo ''
done

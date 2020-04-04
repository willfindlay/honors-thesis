#! /bin/bash

TRIALS=5
KERNEL_SOURCE=/var/tmp/linux

OUTFILE=$1
TEMP_FILE=`mktemp`
TIMEFORMAT="%U %S %R"

[[ -z $1 ]] && { echo "Usage: $0 OUTFILE"; exit -1; }

build_kernel()
{
    cd "$KERNEL_SOURCE"
    make clean
    make -j `nproc`
} 2>&1

run_experiment()
(
    echo "Clearing $TEMP_FILE"
    > "$TEMP_FILE"
    echo "Running experiment..."
    for i in $(seq 1 $TRIALS); do
        echo "Running trial $i..."
        (time "build_kernel") 2>>"$TEMP_FILE"
    done
    awk 'BEGIN {printf "%12s %12s %12s\n", "USER", "SYSTEM", "ELAPSED"} {printf "%12.2f %12.2f %12.2f\n", $1, $2, $3}' "$TEMP_FILE" > $OUTFILE
)

run_experiment

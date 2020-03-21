#! /usr/bin/env bash

LAT_SYSCALL=$1
REPS=${2:-10}

FSDIR=/var/tmp
STAT=$FSDIR/lmbench
mkdir $FSDIR 2>/dev/null
touch $STAT 2>/dev/null
if [ ! -f $STAT ]
then	echo "Can't make a file - $STAT - in $FSDIR" >> ${OUTPUT}
    touch $STAT
    exit 1
fi

date
sleep 1
for (( i=0; i<$REPS; i++ )); do
    echo "Test $i..."
    $LAT_SYSCALL null
    $LAT_SYSCALL read
    $LAT_SYSCALL write
    $LAT_SYSCALL stat $STAT
    $LAT_SYSCALL fstat $STAT
    $LAT_SYSCALL open $STAT
    echo ''
done

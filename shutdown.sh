#!/bin/sh

echo -n $"Shutting down mi-apiroot: "
pids=(`ps -ax | grep python3.6 | grep apiroot | awk '{print $1}'`)
for procid in ${pids[@]}
    do
    kill -15 $procid
    rv=$?
done
echo
[ $rv -eq 0 ]

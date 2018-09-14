#!/bin/sh

echo -n $"Shutting down mi-docroot: "
pids=(`ps -ax | grep python3.6 | grep docroot | awk '{print $1}'`)
for procid in ${pids[@]}
    do
    kill -15 $procid
    rv=$?
done
echo
[ $rv -eq 0 ]

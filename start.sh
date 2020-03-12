#!/bin/sh

exec="/usr/local/python3.6.2/bin/python3.6 apiroot.py $1 $2 >> /var/log/apiroot.log 2>&1 &"

cd /var/lib/mi-apiroot
echo -n $"Stating mi-apiroot: "
eval $exec
rv=$?
echo
[ $rv -eq 0 ]
pids=`ps aux | grep python3.6 | grep apiroot | awk '{print $1}'`

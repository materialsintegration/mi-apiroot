#!/bin/sh

exec="python3.6 docroot.py $1 $2 >> /var/log/docroot.log 2>&1 &"

cd /var/lib/mi-docroot
echo -n $"Stating mi-docroot: "
eval $exec
rv=$?
echo
[ $rv -eq 0 ]
pids=`ps -ax | grep python3.6 | grep docroot | awk '{print $1}'`

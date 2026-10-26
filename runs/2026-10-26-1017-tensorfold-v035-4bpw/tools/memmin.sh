#!/bin/bash
# memmin.sh SECONDS OUT : sample MemAvailable every 0.5 s, keep the minimum (GiB) and a 5 s trace
end=$(( $(date +%s) + $1 )); min=999999999; : > $2.trace
while [ $(date +%s) -lt $end ]; do
  a=$(awk '/MemAvailable/{print $2}' /proc/meminfo); [ $a -lt $min ] && min=$a
  echo "$(date +%T) $a" >> $2.trace; echo "min_gib $(awk -v m=$min 'BEGIN{printf "%.2f", m/1048576}')" > $2
  sleep 0.5
done

#!/bin/bash
# start_pool.sh POOL (on the head node): the fleet endpoint (both rails, patch 0004) with the shared KV pool set to POOL positions.
# Writes a copy of config.fleet-8000-rail2-p4.env with the three pool values replaced, then starts it like start_fleet_rail2_p4.sh.
# POOL must be at least --context (1048576); 16777216 = 16 streams x 1M is the most the 16 streams can use.
P=${1:?usage: start_pool.sh POOL}
sed -e "s/2097152/$P/g" /var/tmp/tf1017/config.fleet-8000-rail2-p4.env > /var/tmp/tf1017/config.fleet-8000-pool.env
export DSV41_CONFIG=/var/tmp/tf1017/config.fleet-8000-pool.env
date -u
/var/tmp/tf1017/rail2_all.sh add
/var/tmp/tf1017/recipe/scripts/serve.sh start
echo "START rc=$? pool=$P"
date -u

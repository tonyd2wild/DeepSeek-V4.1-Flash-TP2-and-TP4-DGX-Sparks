#!/bin/bash
# start_fleet_v035.sh [POOL] (on Reddie): fleet :8000 on bertholomus recipe v0.3.5 + 4.0 bpw, both RoCE rails. POOL overrides the window (default 20971520).
P=${1:-20971520}
sed -e "s/20971520/$P/g" /var/tmp/tf4/config.fleet-8000-v035.env > /var/tmp/tf4/config.fleet-8000-v035-run.env
export DSV41_CONFIG=/var/tmp/tf4/config.fleet-8000-v035-run.env
date -u
/var/tmp/tf1017/rail2_all.sh add
/var/tmp/tf4/recipe/scripts/serve.sh start
echo "START rc=$? pool=$P"
date -u

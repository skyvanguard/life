#!/bin/bash
# Heartbeat loop. Interval from HEARTBEAT_INTERVAL (seconds). Kept in a file so
# the container CMD stays quoting-simple (`bash /opt/data/heartbeat/loop.sh`).
sleep 45
while true; do
  bash /opt/data/heartbeat/tick.sh
  sleep "${HEARTBEAT_INTERVAL:-1800}"
done

#!/bin/sh
# Smoke-test a running/deployed Worker.  Usage: BASE=https://... DEVICE_KEY=... READ_KEY=... ./test-curl.sh [temp_f]
BASE=${BASE:-http://localhost:8787}
curl -s -XPOST "$BASE/reading" -H "X-Device-Key: $DEVICE_KEY" -H 'content-type: application/json' \
  -d "{\"temp_f\":${1:-70},\"rail_v\":12.8,\"batt_v\":4.1,\"rssi\":-80}"; echo
sleep 2
curl -s "$BASE/latest" -H "X-Read-Key: $READ_KEY"; echo

#!/bin/sh

INTERVAL="${COLLECTD_INTERVAL:-60}"
HOSTNAME="${COLLECTD_HOSTNAME:-$(hostname -f)}"

while sleep "$INTERVAL"
do
  codec_value=$(cat /data/kmb/codec)
  vpu_value=$(cat /data/kmb/vpu)
  echo "PUTVAL \"$HOSTNAME/kmb_vpu/gauge\" interval=$INTERVAL N:$vpu_value"
  echo "PUTVAL \"$HOSTNAME/kmb_codec/gauge\" interval=$INTERVAL N:$codec_value"
done

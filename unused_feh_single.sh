#!/bin/bash

image_file="$1"
feh -Z -F -Y -D 5 "$image_file" &
pid=$!  # get process ID of feh

# sleep just has to be 2 seconds longer than python's sleep before it launches
# another feh instance that'll overwrite this one
sleep 5

kill $pid

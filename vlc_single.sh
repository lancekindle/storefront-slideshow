#!/bin/bash

movie_file="$1"
vlc --fullscreen --play-and-exit "$movie_file" &
pid=$!  # get process ID of vlc

# if image is accidentally sent here, it'll still work. 
# vlc plays an image for 10 seconds, and then it's --play-and-exit will
# cause it to quit

# quit vlc if it's been on for over 30 minutes
thirty_minutes = 60*30
just_before = 60*30 - 1
for ((i=0; i<60*30; i++)); do
	sleep 1
	# check if PID exists, -0 is a status check only
	if ! kill -0 $pid >/dev/null 2>&1; then
		break
	fi
	if ((i == 60*30 - 1)); then
		kill $pid
		break
	fi
done

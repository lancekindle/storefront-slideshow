Designed to show a slideshow on a TV for confluent

Clone this repo on a raspberry pi (make sure it's connected to wifi) and then run
sudo setup.sh

a few extra manual config changes will need to be made (as printed at end of running setup.sh)

The script will install cron jobs to:
Connect to confluent's shared pictures directory at //10.10.10.10/Users/slideshow
Turns the TV on at 8am, and off at 10PM. Those hours are in setup.py  (.py, not .sh).
The main script (run.py) gets run ONCE after the tv turns on, which displays a new picture every 5 seconds (see run.py > DELAY_BETWEEN_PICS).
Script is intended to run forever, but gets terminated (by stop.sh) when the TV turns off (tv_off.sh).

. Somewhere in /boot/config.txt on the SD card you can add an option to rotate the display, so that it faces the correct way.
(rotation is NOT done with this script, you must do it manually)

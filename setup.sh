sudo apt install inotify-tools cifs-utils smbclient
sudo apt install vim vlc feh rsync cec-utils xcompmgr xdotool wmctrl compton

pip install python-vlc

echo "---------------------------------"
echo "---------------------------------"
echo "---------------------------------"
echo "you need to set settings on panel to make it minimize to 0 pixels when not in use (as fading between pictures shows the application panel otherwise"
echo "---------------------------------"
echo "also need to edit /etc/lightdm/lightdm.conf and add under the [Seat:*] section"
echo "xserver-command=X -s 0 dpms"
echo "(it's disabling the screen blanking)"

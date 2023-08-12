# this is for mounting share that holds pictures. Then they are copied using rsync
sudo mkdir /tmp/smb
sudo mount -t cifs //10.10.10.10/public/Users/slideshow /tmp/smb -o guest,vers=2.0

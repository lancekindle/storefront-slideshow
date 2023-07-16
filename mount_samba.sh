# this is for mounting share that holds pictures. Then they are copied using rsync
sudo mount -t cifs //10.10.10.10/public/slideshow /mnt/smb -o guest,vers=2.0

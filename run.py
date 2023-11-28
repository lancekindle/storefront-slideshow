#! /usr/bin/python

'''
    this program will display images and videos in a slideshow. It uses FEH and VLC. It also launches an image sync while it runs, to continue copying images.
    At this point in time, it will not see those newly synced images until another run
'''

import vlc
import time
import subprocess
import os
import getpass

SCRIPT_HOME = os.path.dirname(os.path.abspath(__file__))
DELAY_BETWEEN_PICS = 5

def get_screen_resolution():
    xrandr = subprocess.run("xrandr | grep -w connected | awk '{print $4}' | cut -d'+' -f1", shell=True, capture_output=True, text=True)
    return xrandr.stdout.strip()

def enable_smooth_effects():
    # starts program that smooths transition between windows
    subprocess.run('pkill compton', shell=True)
    sub = subprocess.Popen(['compton', '-cfD', '10'])
    pass

RESOLUTION = get_screen_resolution()
# FEH can be used to show a slideshow. But here we abuse it to show one image then re-launch FEH. The reason for doing this is that each time we launch a new instance of feh,
# it'll materialize with a smooth, subtle fade-in affect due to compton (above program). I really worked hard to make this happen, as I think it's looks much better
# than FEH's sudden transition between images during a slideshow.
FEH = ['feh', f'-ZYD {DELAY_BETWEEN_PICS*2}', '--geometry', f'{RESOLUTION}', '--auto-zoom', '--borderless', '--scale-down', '--image-bg', 'black', '--on-last-slide=quit']

# variables used for showing images in a seamless manner
global time_image_displayed
global showing_image
global obscured_image
time_image_displayed = time.time() - DELAY_BETWEEN_PICS
showing_image = subprocess.Popen(['sleep', '0'])
obscured_image = subprocess.Popen(['sleep', '0'])


def download_media(local_uri, local_folder):
    # if the trailing slashes are missing, rsync may copy local_uri source folder inside the local folder
    if not local_uri.endswith('/'):
        local_uri += '/'
    if not local_folder.endswith('/'):
        local_folder += '/'
    sub = subprocess.Popen(['rsync', '-av', f'{local_uri}', f'{local_folder}'])
    return  # begin slideshow while files download

def play_video(video_file):
    sub = subprocess.Popen(['bash', f'{SCRIPT_HOME}/vlc_single.sh', video_file])
    sub.wait()  # don't return until video finishes playing (and program exits)

def trigger_file_watcher(image):
    """ a test that file watcher sees this new copied file that I add """
    return  # it works! Don't need to do this anymore
    subprocess.Popen(['cp', image, '9' + image])

def show_picture(image):
    global time_image_displayed
    global showing_image
    global obscured_image

    # trigger_file_watcher(image)  # enable to endlessly copy a file -- easy way to test that file-watcher works
    
    time_remains_before_next_pic = DELAY_BETWEEN_PICS - (time.time() - time_image_displayed)
    if time_remains_before_next_pic > 0:
        time.sleep(time_remains_before_next_pic)

    # we launch new FEH instance over still-displaying instance because we cannot guarantee how long it'll take to load image. We want a seemless transition between images.
    obscured_image = showing_image  # currently shown image is about to be obscured by new feh instance.
    showing_image = subprocess.Popen(FEH + [image])
    time_image_displayed = time.time()
    

BANNED_FILETYPES = ['sh', 'py']

def find_new_files(file_list, slideshow_folder, shown_files, file_watcher):
    if not file_list or file_watcher.stdout.read():
        file_list = os.listdir(slideshow_folder)
        file_list = [f for f in file_list if f not in shown_files]
        file_list = [f for f in file_list if os.path.isfile(f) and not f.startswith('.')]  # do not want folders or hidden files
        file_list.sort()
        file_list.reverse()  # oldest filenames will be .pop()'d first
    return file_list

def show_all_files(slideshow_folder):
    file_watcher = subprocess.Popen(['inotifywait', '-e', 'create', '-e', 'delete', '-m', '-r', slideshow_folder], stdout=subprocess.PIPE)  # watch for new files / deleted files
    os.set_blocking(file_watcher.stdout.fileno(), False)  # on unix systems only; ensures that stdout.read() won't block if there's no output
    shown_files = set()  # keep track of shown files
    os.chdir(slideshow_folder)
    print('at file list')
    file_list = find_new_files([], slideshow_folder, shown_files, file_watcher)
    
    print('file_list', file_list)
    image_files = []
    while file_list:
        file = file_list.pop()  # since we pop, we show larger filenames first
        name_and_ext = file.split('.')
        filetype = name_and_ext[-1]
        if filetype in BANNED_FILETYPES:
            shown_files.add(file)
        elif filetype.lower() in ['jpggglg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'svg', 'webp', 'heic', 'heif', 'raw']:
            show_picture(file)
            shown_files.add(file)
        else:  # vlc will show a picture too, but it's not as clean
            video_file = os.path.join(slideshow_folder, file)
            play_video(video_file)
            shown_files.add(file)

        file_list = find_new_files(file_list, slideshow_folder, shown_files, file_watcher)


if __name__ == '__main__':
        enable_smooth_effects()
        rsync_download_from = r'/tmp/smb/'  # on startup, this directory will be a SAMBA share
        USER = getpass.getuser()
        slideshow_folder = f'/home/{USER}/Pictures'  # where pictures get put and parsed
        for _ in range(2):
            download_media(rsync_download_from, slideshow_folder)
            show_all_files(slideshow_folder)
    


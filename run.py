#! /usr/bin/python

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

RESOLUTION = get_screen_resolution()
FEH = ['feh', f'-ZYD {DELAY_BETWEEN_PICS*2}', '--geometry', f'{RESOLUTION}', '--auto-zoom', '--borderless', '--scale-down', '--image-bg', 'black', '--on-last-slide=quit']

def enable_smooth_effects():
    # starts program that smooths transition between windows
    subprocess.run('pkill compton', shell=True)
    sub = subprocess.Popen(['compton', '-cfD', '10'])
    pass

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

def play_slideshow(image_files, shown_files):
    shown_files.update(*image_files)
    trigger_file_watcher(image_files[0])
    # split images so that alternating between feh instances will show images in order
    half1 = image_files[::2]
    half2 = image_files[1::2]
    # in order for FEH to work, an image has to be supplied as last argument
    sub = subprocess.Popen(FEH + [image_files[0]])
    time_image_displayed = time.time()
    for image in image_files[1:]:
        old_sub = sub
        time_remains_before_next_pic = DELAY_BETWEEN_PICS - (time.time() - time_image_displayed)
        if time_remains_before_next_pic > 0:
            time.sleep(time_remains_before_next_pic)
        sub = subprocess.Popen(FEH + [image])
        time_image_displayed = time.time()  # reset timer
        if image == image_files[-1]:
            # for last file, we can exit early, but return old_sub, to make sure that finishes before we begin next set of images
            image_files.clear()
            return old_sub
        old_sub.wait()  # wait for old (not showing) feh to exit. This will be after 10 seconds of running, 5 seconds of those was with the new feh displaying it's new image
    # we should never get here, but just in case
    image_files.clear()
    return

banned_filetypes = ['sh', 'py']

def show_all_files(slideshow_folder):
    file_watcher = subprocess.Popen(['inotifywait', '-e', 'create', '-e', 'delete', '-m', '-r', slideshow_folder], stdout=subprocess.PIPE)  # watch for new files / deleted files
    os.set_blocking(file_watcher.stdout.fileno(), False)  # on unix systems only; ensures that stdout.read() won't block if there's no output
    file_watcher.stdout.read()  # clear any initial output
    shown_files = set()  # keep track of shown files
    os.chdir(slideshow_folder)
    file_list = os.listdir(slideshow_folder)
    file_list.sort()  # python sort by name  (here's where we could add additional info like created as well to prioritize newer pictures)
    file_list.reverse()  # so that smaller numbers are shown first
    image_files = []
    still_running = None  # for holding a process that can get .wait()'d on
    while file_list:
        # loop through files, creating a list of 10 images to display at once with feh, then display them. Or display images gathered and then play video if video was found. Or display remaining images if that's all there is
        file = file_list.pop()
        if file in shown_files:
            file_list = [f for f in file_list if f not in shown_files]
        valid = True  # set to False if it's not a valid image or video file
        video = False  # set to True to show images first, then play video
        # we do not want folders or hidden files
        if not os.path.isfile(file) or file.startswith('.'):
            valid = False
        name_and_ext = file.split('.')
        filetype = name_and_ext[-1]
        if filetype in banned_filetypes:
            valid = False
        if valid and filetype.lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'svg', 'webp', 'heic', 'heif', 'raw']:
            image_files.append(file)
            shown_files.add(file)
        elif valid:  # vlc will show a picture too, but it's not as clean
            video = True
            shown_files.add(file)

        # now show the images
        # showing the images also clears the list, and adds to shown_files
        if image_files and not file_list:
            still_running = play_slideshow(image_files, shown_files)
        if len(image_files) >= 10:
            still_running = play_slideshow(image_files, shown_files)
        if video and image_files:
            still_running = play_slideshow(image_files, shown_files)
        if video:
            video_file = os.path.join(slideshow_folder, file)
            play_video(video_file)
        
        # now we've either shown all the files, or we need to keep looping
        # while final image (still_running) shows, we refetch folder in case rsync downloaded new ones
        if still_running:
            are_new_files = file_watcher.stdout.read()
            if len(image_files) == 0 and are_new_files:
                print(are_new_files)
                file_list = os.listdir(slideshow_folder)
                file_list = [f for f in file_list if f not in shown_files]
                file_list.sort()
            still_running.wait()
            still_running = None


if __name__ == '__main__':
        enable_smooth_effects()
        rsync_download_from = r'/mnt/smb/'
        USER = getpass.getuser()
        slideshow_folder = f'/home/{USER}/Pictures'  # where pictures get put and parsed
    #while True:
        download_media(rsync_download_from, slideshow_folder)
        show_all_files(slideshow_folder)
        


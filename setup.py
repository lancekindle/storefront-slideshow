import getpass
from crontab import CronTab
import os
USER = getpass.getuser()
if USER != 'root':
    print('WARNING! NEEDS TO RUN AS ROOT TO SCHEDULE SCRIPTS')
SCRIPT_HOME = os.path.dirname(os.path.abspath(__file__))

tv_on_hours=[8,]
tv_off_hours=[22,]
# time for turning tv on and off. Can put in multiple times

with CronTab(user='root') as cron:
    cron.remove_all(comment='auto-added')
    samba_script = os.path.join(SCRIPT_HOME, 'mount_samba.sh')
    job = cron.new(command=samba_script, comment='auto-added')
    job.every_reboot()


    for on_hour in tv_on_hours:
        job = cron.new(command=os.path.join(SCRIPT_HOME, 'tv_on.sh'), comment='auto-added')
        job.hour.on(on_hour)
        slideshow = cron.new(command=os.path.join(SCRIPT_HOME, 'run.py'), comment='auto-added')
        slideshow.hour.on(on_hour)
    
    for off_hour in tv_off_hours:
        job = cron.new(command=os.path.join(SCRIPT_HOME, 'tv_off.sh'), comment='auto-added')
        job.hour.on(off_hour)
        kill_slideshow = cron.new(command=os.path.join(SCRIPT_HOME, 'stop.sh'), comment='auto-added')
        kill_slideshow.hour.on(off_hour)

    


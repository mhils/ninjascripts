from configobj import ConfigObj
from validate import Validator
from time import time, sleep
from datetime import timedelta
import xml.etree.ElementTree as ET
from os.path import isdir, isfile
import subprocess, StringIO, sys

config = ConfigObj("backuphelper.cfg",configspec=StringIO.StringIO("""
lastBackup = float(default=0)
backupInterval = integer(default=604800) #week, 60*60*24*7
[DirSyncPro]
Jobfile = string(default="Job.dsc")
Executable = string(default="java.exe")
Arguments = string_list(default=list('-Xmx512M', '-jar', 'C:\Users\user\DirSync Pro\dirsyncpro.jar', '/sync', '/quit'))
"""))
config.validate(Validator(),copy=True)
config.write()
lastBackup = timedelta(seconds=(time() - config['lastBackup']))
if(config['lastBackup'] == 0):
    print "Last Backup: Never"
else:
    print "Last Backup: "+str(lastBackup)+ " ago."

if(lastBackup > timedelta(seconds=config['backupInterval'])):
    print "A new Backup is necessary."
    if(not isfile(config['DirSyncPro']['Jobfile'])):
        print "Fatal Error: "+config['DirSyncPro']['Jobfile']+" not found."
        raw_input("")
	sys.exit(1)
    doc = ET.parse(config['DirSyncPro']['Jobfile'])
    lastMissingPaths = []
    while True:
        missingPaths = []
        for node in doc.findall("job"):
            for path in [node.get("src"),node.get("dst")]:
                if not isdir(path):
                    missingPaths.append(path)
        if(len(missingPaths) == 0):
            break;
        if(lastMissingPaths != missingPaths):
            print "Please connect the following directories:"
            for path in missingPaths:
                print path
            lastMissingPaths = missingPaths
        sleep(1)
    print "Starting DirSyncPro:"
    args = []
    args.append(config["DirSyncPro"]["Executable"])
    for arg in config["DirSyncPro"]["Arguments"]:
        args.append(arg)
    args.append(config['DirSyncPro']['Jobfile'])
    print args
    retcode = subprocess.call(args)
    if((retcode == 0)or(retcode == 1)):
        config['lastBackup'] = time()
        config.write()
        if(retcode==1):
            print "Finished with non-fatal ERRORS!"
	else:
            print "Backup SUCCESSFUL!"
	raw_input("")
	sys.exit(1)
    else:
	if(retcode==2):
            print "Backup stopped due to FATAL ERRORS!"
	raw_input("")
	sys.exit(1)
else:
    print "No backup necessary."
    sys.exit(0)
sys.exit(1)

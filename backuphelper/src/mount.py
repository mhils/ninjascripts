from win32com.client import Dispatch
from configobj import ConfigObj
from validate import Validator
import os, getpass, subprocess, warnings, win32api, os.path, StringIO

selfconfig = ConfigObj("mount.cfg",configspec=StringIO.StringIO("""
Executable = string(default="C:/Program Files/TrueCrypt/TrueCrypt.exe")
"""))
selfconfig.validate(Validator(),copy=True)
selfconfig.write()

fso = Dispatch('scripting.filesystemobject')
config = ConfigObj(configspec=['[keyfiles]','[volumes]'])
config["keyfiles"] = {}
config["volumes"] = {}
class TruecryptInterface:
    def __init__(self,tcpath):
        self._tcpath = tcpath
    def mountVolume(self,harddisk,partition,driveletter,keyfiles,password):
        args = [self._tcpath,
                "/volume","\Device\Harddisk"+harddisk+"\Partition"+partition,
                "/letter",driveletter,
                "/password",password,
                "/beep",        #Beep after a volume has been successfully mounted or dismounted.
                "/c","n",       #disable password cache
                "/wipecache",   #why not wipe the password cache?
                "/silent",      #suppresses interaction with the user
                "/quit"]        #Automatically perform requested actions and exit
        for keyfile in keyfiles:
            args.append("/k")
            args.append(keyfile)
        #DEBUG print args
        return subprocess.call(args)

class DriveManager:
    def __init__(self):
        self._alldrives = frozenset(map(lambda x: chr(x),range(ord('D'), ord('Z')+1)))
        self._blockedDrives = set()
        self._wishlist = set()
    def blockDrive(self,drive):
        self._blockedDrives.add(drive)
        return True
    def addDriveToWishList(self, wishlist):
        if(type(wishlist).__name__ == 'list'):
            wishlist = set(wishlist)#type becomes set
        if(type(wishlist).__name__ == 'set'):
            self._wishlist |= wishlist
        elif(type(wishlist).__name__ == 'str'):
            self._wishlist.add(wishlist)
        else:
            raise SyntaxError("Argument not applicable")
        return True
    def getFirstAvailableDrive(self, wanted):
        if (wanted not in self._blockedDrives):
            return wanted
        else:
            freedrives = self._alldrives - self._blockedDrives - self._wishlist
            if (len(freedrives) > 0):
                return list(freedrives)[0]
            else:
                raise BaseException("Too many drives mounted.")              

class PasswordManager:
    def __init__(self):
        self.passwords = {}
        
    def _initPass(self,passid):
        if(passid not in self.passwords):
            self.passwords[passid] = {"attempts":0}
            
    def _promptPass(self,passid):
        self._initPass(passid)
        try:
            win32api.SetConsoleTitle("mount.py - password required: "+ passid)
        except:
            warnings.warn("Cannot change window title - Running in IDLE?")
        self.passwords[passid]["val"] = getpass.getpass(passid+": ")
        print "Ok!"
        self.passwords[passid]["attempts"] = self.passwords[passid]["attempts"] + 1
    def _hasPass(self,passid):
        self._initPass(passid)
        if("val" in self.passwords[passid]):
            return True
        return False
    def getPass(self,passid):
        if not(self._hasPass(passid)):
            if(self.passwords[passid]["attempts"] < 3):
                self._promptPass(passid)
            else:
                raise NameError(" Too many attempts for password with id "+passid)
        return self.passwords[passid]["val"]
    def delPass(self,passid):
        self._initPass(passid)
        del self.passwords[passid]["val"]
        return True

driveman = DriveManager()
passman = PasswordManager()
truecrypt = TruecryptInterface(selfconfig["Executable"])

#read cfg files
for i in fso.Drives:
    driveman.blockDrive(i.DriveLetter)
    if i.DriveType != 4:#DriveType 4 is CD, I don't like my cddrive to power up
        configpath = i.DriveLetter+":/truecrypt.cfg"
        if(os.path.exists(configpath)):
           #print "TrueCrypt config on drive "+i.DriveLetter
           driveconfig = ConfigObj(configpath)

           #keyfiles
           for k in driveconfig.get("keyfiles",{}):
               driveconfig.get("keyfiles",{})[k] = i.DriveLetter + ":/" + driveconfig.get("keyfiles",{}).get(k)
           config["keyfiles"].update(driveconfig.get("keyfiles",{}))

           #volumes
           for key in driveconfig.get("volumes",{}).iterkeys():
               volume = driveconfig.get("volumes").get(key)
               driveman.addDriveToWishList(volume.get("mountto","A"))
               volume["cfgdrive"] = i.DriveLetter
               if(type(volume["keyfiles"]).__name__ == 'str'):
                   volume["keyfiles"] = [volume["keyfiles"],]
               if(volume.get("name",None) == None):
                   volume["name"] = key
           config["volumes"].update(driveconfig.get("volumes",{}))


for volume in config["volumes"].itervalues():
    if(set(volume["keyfiles"]) <= set(config["keyfiles"].iterkeys())):
        thiskeyfiles = map(lambda id: config["keyfiles"][id],volume["keyfiles"])
        thisdriveletter = driveman.getFirstAvailableDrive(volume.get("mountto","A"))
        thispass  = passman.getPass(volume["pass"])
        try:
            for harddisk in range(1,8):
                result = truecrypt.mountVolume(str(harddisk),volume["partitionNo"],thisdriveletter,thiskeyfiles,thispass)
                if(result == 0):
                    if(os.path.isdir(thisdriveletter+":/")):
                        driveman.blockDrive(thisdriveletter)
                        print volume["name"] + " mounted to " + thisdriveletter
                        raise StopIteration()
                    #TODO: TrueCrypt returns exit code 0 for already mounted volumes. Current Bruteforce technique doesn't consider sameHD, so the exit code might be irritating
        except StopIteration:
            pass
    else:
       warnings.warn("Cannot mount volume because some keyfiles are missing:" +
                     ", ".join(list(set(volume["keyfiles"]) - set(config["keyfiles"].iterkeys()))))
#print "keyfiles"
#print config["keyfiles"]
#print "volumes"
#print config["volumes"]
print "Finished!"

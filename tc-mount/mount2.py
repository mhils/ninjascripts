import json, getpass, warnings
from os.path import exists

class Config:
    def __init__(self):
        self._config = {'keyfiles':{},'volumes':{},'truecrypt':{}}

    def process(self,path):
        with open(path, 'r') as f:
            config = json.load(f)
            confdir = os.path.split(path)[0]

            #FIXME: x[1] is not sufficient as it might be a dict in case of the drive
            #maybe introduce new filetypes?
            #Expand path for attributes starting with "."
            def expandPath(x):
                path = x[1]
                if path[:1] == "." or not exists(path):
                    rpath = os.path.join(confdir,path)
                    if exists(rpath):
                        path = rpath
                return (x[0],path)
            
            #merge
            for attr in ["keyfiles", "volumes", "truecrypt"]:
                self._config[attr] = dict(self._config[attr].items() + map(expandPath,config.get(attr,{}).items()))
                
    def getTrueCryptExecutables(self):
        return self._config['truecrypt']
    def getVolumes(self):
        return self._config["volumes"]
    def getKeyfiles(self):
        return self._config["keyfiles"]

class TrueCryptInterface:
    def __init__(self, config):
        self._config = config

    def _getExecutable(self):
        return reduce(lambda x,y:
                      y if not exists(x[1]) else
                      x if not exists(y[1]) else
                      x if x[0] > y[0] else
                      y,
                      self._config.getTrueCryptExecutables().items())

    def _run(self,args):
        args.insert(0,_getExecutable())
        args.extend([
            "/silent",      #suppresses interaction with the user
            "/quit"         #Automatically perform requested actions and exit
            ])
        #print args
        return subprocess.call(args)
        
    def mount(self,volume,letter,keyfiles,password):
        args = ["/volume",volume,
                "/letter",driveletter,
                "/password",password,
                #"/beep",       #Beep after a volume has been successfully mounted or dismounted.
                "/c","n",       #disable password cache
                "/h","n"]       #disable history
        for keyfile in keyfiles:
            args.extend(["/k",keyfile])
        return self._run(args)
    
    def unmount(self,letter,force=False):
        self._run(["/dismount",letter].extend(["/force"] if force else []))

class PasswordManager:
    def __init__(self):
        self._passwords = {}

    def _initPass(self,passId):
        if(passId not in self._passwords):
            self._passwords[passId] = {"attempts":0}
    def _hasPass(self,passId):
        if(passId in self._passwords and "val" in self._passwords[passId]):
            return True
        return False

    def _prompt(self,passId):
        #try to set window title
        try:
            import win32api
            try:
                win32api.SetConsoleTitle("mount.py - password required: "+ passid)
            except:
                warnings.warn("Cannot change window title - Running in IDLE?")
        except ImportError:
            pass
        self._initPass(passId)
        self._passwords[passId]["val"] = getpass.getpass(passId+": ")
        print "Ok!"
        self._passwords[passId]["attempts"] += 1
        
    def getPass(self,passId):
        if not(self._hasPass(passId)):
            if(self._passwords[passId]["attempts"] < 3):
                self._prompt(passId)
            else:
                raise Exception('Too many attempts for password "'+passId+'"')
        return self.passwords[passId]["val"]
    
    def declareInvalid(self,passId):
        del self.passwords[passid]["val"]

class DriveManager():
    pass
    #TODO

conf = new Config()
#TODO: go through all configs without windows os.path.isdir warning

for(v in conf.getVolumes()):
    volume = v[1]
    if(set(volume.get("keyfiles",[])).issubset(conf.getKeyfiles().keys()):
       keyfiles = map(lambda x: conf.getKeyfiles()[x],volume.get("keyfiles",[]))
       letter = volume.get("mountto","X")
       password = passManager.getPass(volume["password"])

       #TODO: mount
       
    else:
       warnings.warn("Cannot mount volume because some keyfiles are missing:" +
                     ", ".join(list(set(volume.get("keyfiles",[])) - set(conf.getKeyfiles().keys()))))

x = PasswordManager()
print x._hasPass("foo")
x._prompt("foo")
print x._hasPass("foo")

            

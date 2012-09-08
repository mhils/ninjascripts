from distutils.core import setup
import py2exe, sys

backuphelper = "./src/backuphelper.py"
mount = "./src/mount.py"

sys.argv.append('py2exe')

op = {
          'py2exe':{
              'bundle_files':1,
              'dist_dir': 'dist',
              'dll_excludes': [ "mswsock.dll", "powrprof.dll" ],
              }
}

#change setup order to avoid icon bug
"""
setup(
      options = op,
      console = [
          {
              "script":backuphelper,
              "icon_resources": [(0, "icon_backup.ico")]
           }],
      zipfile = None
      )"""
setup(
      options = op,
      console = [
          {
              "script":mount,
              "icon_resources": [(1, "icon_mount.ico")]
           }],
      zipfile = None
      )

	  


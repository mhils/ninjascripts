import subprocess
import os.path

for executable in ["backuphelper","tc-mount"]:
    args = ["python",
            "-O",
            "vendor/PyInstaller/pyinstaller.py",
            "--out="+os.path.abspath("./build"),
            "--onefile"]
    icon = os.path.abspath(executable+"/icon.ico")
    if os.path.isfile(icon):
        args.append("--icon="+icon)
    args.append(executable+"/"+executable+".py")
    subprocess.call(args)
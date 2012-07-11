import win32gui, win32con, win32api, time

#This scripts makes WinRaR continue extracting a split archive
#if missings parts appear on the file system (e.g. downloaded).

#Restrictions:
#WinRaR with German Locale
#Win32/64

while True:
    def winEnumHandler(hwnd,ctx):
        global nextVolume, mainWindow
        title = win32gui.GetWindowText( hwnd )
        if(title.find("Entpacke") >= 0):
            mainWindow = hwnd
        if(title.find("chste Volumen wird ben") >= 0):
            nextVolume = hwnd
    nextVolume = mainWindow = 0
    win32gui.EnumWindows( winEnumHandler, None )
    if(mainWindow <= 0):
        break
    if(nextVolume > 0):
        win32api.PostMessage(nextVolume, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
        win32api.PostMessage(nextVolume, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

    time.sleep(5)
        

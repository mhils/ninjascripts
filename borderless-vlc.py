from win32gui import *
from win32con import *
from win32api import *

#
#  The projectors screen cannot be used completely,
#  as there is an window on the left. Projector is on
#  minimum zoom already.
#  Solution: Black background + resized VLC.
#
#  +-------------+
#  |             |
#  |  projector  |
#  |  1280x800   |
#  +-------------+
#  |             |
#  | main screen |
#  |             |
#  +-------------+

TOP = -800
LEFT = 0
HEIGHT = 800
WIDTH = 1280
VLC_LEFT = 404

#Create black Background screen
def Blackscreen(l,t,w,h):
    """Create a black window rectangle as background"""
    wc = WNDCLASS()
    wc.lpszClassName = 'blackscreen'
    brush = CreateSolidBrush(RGB(0, 0, 0))
    wc.hbrBackground = brush   
    class_atom= RegisterClass(wc)
    hwnd =  CreateWindow(class_atom,
        "black screen",
        WS_POPUP | WS_VISIBLE,
        l,t,w,h, 0, 0, 0, None)
Blackscreen(LEFT, TOP, WIDTH, HEIGHT)

#Hide Taskbar
taskbar = FindWindow("Shell_SecondaryTrayWnd","")
ShowWindow(taskbar, SW_HIDE)

# Make VLC frameless and move it
vlc_windows = []
def enumHandler(hwnd, lParam):
    if IsWindowVisible(hwnd):
        if 'VLC' in GetWindowText(hwnd):
            print GetWindowText(hwnd)
            global vlc_windows
            vlc_windows.append([hwnd, GetWindowLong(hwnd, GWL_STYLE)]) # make backup
            SetWindowLong(hwnd, GWL_STYLE, WS_POPUP | WS_VISIBLE)
            
            MoveWindow(hwnd, VLC_LEFT, TOP, WIDTH-VLC_LEFT, HEIGHT, True)
            BringWindowToTop(hwnd)
EnumWindows(enumHandler, None)



#Undo everything
raw_input("Press ENTER to continue...")
ShowWindow(taskbar, SW_SHOW)
for w in vlc_windows:
    SetWindowLong(w[0], GWL_STYLE, w[1])

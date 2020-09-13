from pywinauto import Desktop
from pywinauto.mouse import click
from pywinauto.keyboard import send_keys
import win32gui

def get_zoom_coords():
    coords = (0, 0)
    def callback(hwnd, extra):
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0] + 100
        y = rect[1] + 50
        if 'Zoom Meeting' in win32gui.GetWindowText(hwnd):
            nonlocal coords 
            coords = (x, y)
    win32gui.EnumWindows(callback, None)
    return coords

def get_zoom_chat_coords():
    coords = (0, 0)
    def callback(hwnd, extra):
        rect = win32gui.GetWindowRect(hwnd)
        if 'Zoom Meeting' in win32gui.GetWindowText(hwnd):
            nonlocal coords 
            coords = (rect[2] - 100, rect[3] - 50)
    win32gui.EnumWindows(callback, None)
    return coords

def focus_zoom():
    desktop = Desktop(backend="uia")
    zoom = desktop['Zoom Meeting']
    click(button='left', coords=get_zoom_coords())
    return desktop, zoom

def get_meeting_tools():
    desktop, zoom = focus_zoom()
    meeting_tools = zoom.child_window(title='ContentLeftPanel').child_window(title='Meeting Tools')
    return meeting_tools

def toggle_raise_hand_status():
    focus_zoom()
    send_keys('%y')

def send_reaction(gesture):
    desktop, zoom = focus_zoom()
    meeting_tools = get_meeting_tools()
    reactions = meeting_tools.child_window(title='Reactions')
    reactions.click() 
    reactions_panel = desktop['Dialog'] # TODO: this could change
    reactions_panel[gesture].click()

# unmuted is True, muted is False
def mic_state(getState):
    meeting_tools = get_meeting_tools()
    unmute = meeting_tools.child_window(title='Unmute, currently muted, Alt+A')
    mute = meeting_tools.child_window(title='Mute, currently unmuted,, Alt+A')
    if mute.exists():
        if (getState):
            return True
        else:
            mute.click()
    else:
        if (getState):
            return False
        else:
            unmute.click()

# video is on is True, video is off is False
def video_state(getState):
    meeting_tools = get_meeting_tools()
    start_video = meeting_tools.child_window(title='start my video, Alt+V')
    stop_video = meeting_tools.child_window(title='stop my video, Alt+V')
    if stop_video.exists():
        if (getState):
            return True
        else:
            stop_video.click()
    else:
        if (getState):
            return False
        else:
            start_video.click()

def send_in_chat(message):
    click(coords=get_zoom_chat_coords())
    new_message = message.replace(' ', '{SPACE}')
    send_keys(new_message + '{ENTER}')

def is_chat_open():
    desktop, zoom = focus_zoom()
    chat = zoom.child_window(title='ContentRightPanel').child_window(title='PChatContainer').child_window(title='Chat')
    if chat.exists():
        return True
    else:
        return False

def open_then_send_in_chat(message):
    focus_zoom()
    send_keys('%H')
    new_message = message.replace(' ', '{SPACE}')
    send_keys(new_message + '{ENTER}')
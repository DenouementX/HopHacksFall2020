from pywinauto import Desktop
from pywinauto.mouse import click
from pywinauto.keyboard import send_keys
import win32gui
import threading
import time
import socket
import re
import gesture_server
from Globals import global_vars


def get_zoom_coords():
    coords = (0, 0)

    def callback(hwnd, extra):
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0] + 10
        y = rect[1] + 10
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
    reactions_panel = desktop['Dialog']  # TODO: this could change
    reactions_panel[gesture].click()


buttons = ['Clap', 'Thumbs Up', 'Heart', 'Joy', 'Open Mouth', 'Tada']


def send_reaction_wrap(gesture_id):
    send_reaction(buttons[gesture_id])


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




if __name__ == '__main__':
    time.sleep(1)

    if global_vars.do_react:
        threading.Thread(target=gesture_server.gesture_function).start()

    TCP_IP = '127.0.0.1'
    TCP_PORT = 5005
    BUFFER_SIZE = 20  # Normally 1024, but we want fast response

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    conn, addr = s.accept()
    print('Connection address:', addr)
    while 1:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break
        data_string = data.decode("utf-8")
        data_list = re.split(":\\s*|\\r\\n", data_string)
        print("received data:", data_list)
        global_vars.acquire()
        print("inside lock from bridge!")
        if data_list[0] == 'react' and global_vars.do_react is True:
            send_reaction_wrap(global_vars.gesture_assignments[int(data_list[1])])
        elif data_list[0] == 'assign':
            global_vars.gesture_assignments[int(data_list[1])] = int(data_list[2])
            print(global_vars.gesture_assignments)
        elif data_list[0] == 'do_react':
            old_do_react = global_vars.do_react
            global_vars.do_react = data_list[1] == '1'
            if not old_do_react and global_vars.do_react:
                threading.Thread(target=gesture_server.gesture_function).start()
        elif data_list[0] == 'do_transcribe':
            global_vars.do_transcribe = data_list[1] == '1'
        global_vars.release()
        print("outside lock from bridge!")
        conn.send(data)
        time.sleep(0.01)
    conn.close()

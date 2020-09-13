import threading
import time
import socket
import re
import gesture_server
import speech_server
import os
import zoom_bridge_functions
from Globals import global_vars


if __name__ == '__main__':
    time.sleep(1)
    
    # This path is outside the repo, one directory above, and down to auth again. This is on purpose. 
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath("../../auth/Ten Thirty Tech Team-a8b956ad1156.json")

    if global_vars.do_react:
        threading.Thread(target=gesture_server.gesture_function).start()
    if global_vars.do_transcribe:
        threading.Thread(target=speech_server.main).start()

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
        print("inside lock from main!")
        if data_list[0] == 'react' and global_vars.do_react is True:
            zoom_bridge_functions.zoom_function_wrap(global_vars.gesture_assignments[int(data_list[1])])
        elif data_list[0] == 'assign':
            global_vars.gesture_assignments[int(data_list[1])] = int(data_list[2])
            print(global_vars.gesture_assignments)
        elif data_list[0] == 'do_react':
            old_do_react = global_vars.do_react
            global_vars.do_react = data_list[1] == '1'
            if not old_do_react and global_vars.do_react:
                threading.Thread(target=gesture_server.gesture_function).start()
        elif data_list[0] == 'do_transcribe':
            old_do_transcribe = global_vars.do_transcribe
            global_vars.do_transcribe = data_list[1] == '1'
            if not old_do_transcribe and global_vars.do_transcribe:
                threading.Thread(target=speech_server.main).start()
        elif data_list[0] == 'do_live':
            global_vars.do_type_transcribe = data_list[1] == '1'

        if data_list[0] == 'query':
            conn.send(bytes(str(global_vars), 'ascii'))
        else:
            conn.send(data)
        global_vars.release()
        print("outside lock from main!")

        time.sleep(0.01)
    conn.close()

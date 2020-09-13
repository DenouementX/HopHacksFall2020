import zmq
from time import sleep
from zoom_bridge_functions import send_reaction
from zoom_bridge_functions import send_in_chat
from zoom_bridge_functions import is_chat_open
from zoom_bridge_functions import toggle_raise_hand_status
from zoom_bridge_functions import mic_state
from zoom_bridge_functions import video_state
from zoom_bridge_functions import open_then_send_in_chat

import threading

context = zmq.Context()

socket = context.socket(zmq.SUB)
socket2 = context.socket(zmq.SUB)

poller = zmq.Poller()
poller2 = zmq.Poller()
poller.register(socket, zmq.POLLIN)
poller2.register(socket2, zmq.POLLIN)

socket.connect("tcp://127.0.0.1:5006")
socket2.connect("tcp://127.0.0.1:6007")

socket.setsockopt_string(zmq.SUBSCRIBE, "")
socket2.setsockopt_string(zmq.SUBSCRIBE, "")

socket.setsockopt(zmq.RCVHWM , 1)
socket2.setsockopt(zmq.RCVHWM , 1)

prev_gesture = ""
consecutive_count = 0
looking_for_text = False

def gesture():
    evts2 = poller2.poll(400)
    if evts2:
        return socket2.recv_string()
    return '0'

def speech():
    evts = poller.poll(400)
    if evts:
        return socket.recv_string()
    return '1'

while True:
    my_gesture = gesture()
    my_speech = speech()
    print(my_gesture)
    print(my_speech)
    if (looking_for_text and my_speech != '1'):
        if not is_chat_open():
            open_then_send_in_chat(my_speech[1:])
        send_in_chat(my_speech[1:])
        looking_for_text = False;
    if (my_gesture == prev_gesture and my_gesture != '0'):
        consecutive_count = consecutive_count + 1
    else:
        consecutive_count = 0
    if (consecutive_count == 5):
        consecutive_count = 0
        if (my_gesture == '0FIVE'):
            looking_for_text = True
        if (my_gesture == '0FOUR'):
            send_reaction('Thumbs Up')
        if (my_gesture == '0SPIDERMAN'):
            send_reaction('Clap')
        if (my_gesture == '0TWO'):
            send_reaction('Tada')
        if (my_gesture == '0ONE'):
            toggle_raise_hand_status()
        if (my_gesture == '0ROCK'):
            mic_state(False)
        if (my_gesture == '0YEAH'):
            video_state(False)

    prev_gesture = my_gesture


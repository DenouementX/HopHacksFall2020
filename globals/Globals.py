import threading

class Globals:
    gesture_assignments = [i for i in range(6)]
    do_react = True
    do_transcribe = False
    lock = threading.Lock()

    def acquire(self):
        self.lock.acquire()

    def release(self):
        self.lock.release()


global_vars = Globals()
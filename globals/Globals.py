import threading

class Globals:
    gesture_assignments = [i for i in range(9)]
    do_react = True
    do_transcribe = True
    do_type_transcribe = False
    lock = threading.Lock()

    def acquire(self):
        self.lock.acquire()

    def release(self):
        self.lock.release()

    def __str__(self):
        return str(self.gesture_assignments) + str(self.do_react) + str(self.do_transcribe) + str(self.do_type_transcribe)


global_vars = Globals()
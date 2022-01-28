import threading
# determines if connected to BS
connected = False
lock = threading.Lock()
radio_lock = threading.Lock()

def log(val):
    print("[AUV]\t" + val)

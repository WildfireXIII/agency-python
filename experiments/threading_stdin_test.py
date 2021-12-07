import sys
from threading import Thread, Lock
import time



def wait_for_input(lock):
    #while True:
    line = sys.stdin.readline()
    lock.acquire()
    print("I got a line!")
    print(line)
    lock.release()


console_lock = Lock()

t1 = Thread(target=wait_for_input, args=(console_lock,))
print(t1.is_alive())
t1.start()

while True:
    time.sleep(1)
    print(f"Nonsense {t1.is_alive()}")


# 
# 
# def print_msg(msg, lock):
#     while True:
#         time.sleep(1)
#         lock.acquire()
#         print(f"This thread was requested to echo: {msg}")
#         lock.release()
#     
# 
# console_lock = Lock()
# t1 = Thread(target=print_msg, args=("test1", console_lock))
# t2 = Thread(target=print_msg, args=("test2", console_lock))
# 
# t1.start()
# t2.start()

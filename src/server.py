from client import Client
import time

if __name__ == '__main__':
    print("Start")
    clients = []
    time_start = time.time()
    for i in range(10):
        c = Client(name=f'Client_{i}')
        clients.append(c)
        c.start()

    for c in clients:
        c.join()

    print("===================")
    print(f"Main Killed {time.time() - time_start}")

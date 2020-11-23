from multiprocessing import Manager
from src.replicator_manager import ReplicatorManager
from src.replicator import Replicator
from src.client import Client
import os

if __name__ == '__main__':
    server_manager = Manager()
    log_lock = server_manager.Lock()
    log_path = 'log/server.log'
    os.system(f'rm -rf {log_path}')

    clients = []
    for i in range(1, 3):
        clients.append(
            Client(
                name=f'Client_{i}',
                ip_replicator_manager='http://0.0.0.0:8000',
                log_server_path=log_path,
                log_server_lock=log_lock
            )
        )

    rm = ReplicatorManager(name='Replicator_Manager', port=8000)
    rm.start()

    for c in clients:
        c.start()
    
    for c in clients:
        c.join()
    rm.join()

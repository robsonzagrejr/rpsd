from src.server.replicator_manager import ReplicatorManager
from src.server.replicator import Replicator

if __name__ == '__main__':
    rm = ReplicatorManager('Replicator_Manager', 8000)
    rm.start()

    rm.join()

from src.server.replicator import Replicator

if __name__ == '__main__':
    replicators = []
    replicators.append(Replicator(name='R1', port=8000))
    replicators.append(Replicator(name='R2', port=8001))

    for r in replicators:
        r.start()

    for r in replicators:
        r.join()

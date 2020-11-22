import time
import json
import random
from flask import Flask, Response, request
from multiprocessing import Process, Queue
from src.server.replicator import Replicator

class ReplicatorManager(Replicator):

    def __init__(self, name, port, n_replicators=2):
        super().__init__(name=name, port=port, server=False)
        self.replicators = []
        for i in range(1, n_replicators+1):
            r = Replicator(name=f'R{i}', port=port+i)
            self.replicators.append(r)
            r.start()

        self.request_queue = Queue()

        self.add_endpoint(endpoint='/', handler=self.get_request, methods=['POST'])

        # Process to solve requests
        Process(target=self.solve_request).start()
        return

    def run(self):
        super().run()
        for r in self.replicators:
            r.join()
        return


    def get_request(self):
        data, status = self.get_data(keys=['request', 'timestamp'])
        if status != 200:
            return data, status
        self.request_queue.put((data['timestamp'], data['request']))
        return f"Request {json.dumps(data)} add to queue :)", 200


    def solve_request(self):
        while True:
            if not self.request_queue.empty():
                print("\n=============================\n")
                _, client_request = self.request_queue.get(0)
                print(f"[self.name] Estou resolvendo {client_request}")
                if client_request['type'] == 'create':
                    self.create_file(data=client_request['data'])
                elif client_request['type'] == 'update':
                    self.update_file(data=client_request['data'])
                elif client_request['type'] == 'append':
                    self.append_file(data=client_request['data'])
                elif client_request['type'] == 'delete':
                    self.delete_file(data=client_request['data'])
                elif client_request['type'] == 'get':
                    self.get_file(data=client_request['data'])

                time.sleep(0.2)




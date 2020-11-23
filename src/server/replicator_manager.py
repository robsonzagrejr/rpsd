from multiprocessing import Process, Queue, Event, Manager
import time
import json
import random
import requests

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
        self.manager = Manager()

        self.add_endpoint(endpoint='/', handler=self.get_request, methods=['POST'])

        # Process to solve requests
        self.solver_process = Process(target=self.solve_request)
        self.solver_process.start()
        return

    def run(self):
        super().run()
        #Kill childs
        self.solver_process.terminate()
        for r in self.replicators:
            r.terminate()
        return


    def get_request(self):
        data, status = self.get_data(keys=['request', 'timestamp'])
        if status != 200:
            return data, status
        event_wait = self.manager.Event()
        #print(f"Request {data['request']}")
        self.request_queue.put((data['timestamp'], data['request'], event_wait))
        event_wait.wait()
        #print(f"Waking {data['request']}")
        return f"Request {json.dumps(data)} add to queue :)", 200


    def make_request(self, replicator, data, rq_type):
        response = requests.post(
                f'http://{replicator.ip}:{replicator.port}/{rq_type}_file',
                json=data
        ) 
        return


    def solve_request(self):
        while True:
            if not self.request_queue.empty():
                #print("\n=============================\n")
                _, client_request, event_wait = self.request_queue.get(0)
                #print(f"[self.name] Estou resolvendo {client_request}")
                #time.sleep(1)
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

                #time.sleep(2)
                #print(f"RESOLVI O {client_request}")
                replicators_request = []
                for replicator in self.replicators: 
                    print(f"Encaminhando {client_request} para {replicator.name}")
                    replicators_request.append(Process(target=self.make_request,
                        args=(replicator, client_request['data'], client_request['type'])))
                for rq in replicators_request:
                    rq.start()
                for rq in replicators_request:
                    rq.join()

                event_wait.set()






from multiprocessing import Process, Queue, Event, Manager
import time
import json
import random
import requests

from src.replicator import Replicator

class ReplicatorManager(Replicator):

    def __init__(self, name, ip, port, log_server_path, log_server_lock, n_replicators=3):
        super().__init__(
            name=name,
            ip=ip,
            port=port,
            log_server_path=log_server_path,
            log_server_lock=log_server_lock,
            server=False
        )
        self.replicators = []
        for i in range(1, n_replicators+1):
            r = Replicator(
                    name=f'Replicator_{i}',
                    ip=self.ip,
                    port=self.port+i,
                    log_server_path=self.log_server_path,
                    log_server_lock=self.log_server_lock
            )
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
        data, status = self.get_data(keys=['request', 'timestamp', 'send_id'])
        if status != 200:
            self.log(data)
            return data, status
        event_wait = self.manager.Event()
        self.log(f"Request from data['send_id'] for {data['request']['type']}: {data['request']['data']}")
        self.request_queue.put(
            (
                data['timestamp'],
                data['send_id'],
                data['request'],
                event_wait
            )
        )
        event_wait.wait()
        #print(f"Waking {data['request']}")
        return f"Request {json.dumps(data)} add to queue :)", 200


    def make_request(self, replicator, client_name, data, rq_type):
        data['send_id'] = self.name
        self.log(f'Sending request {client_name} for {replicator.name}')
        answer = requests.post(
                f'http://{replicator.ip}:{replicator.port}/{rq_type}_file',
                json=data
        ) 
        self.log(f'Answer from [{replicator.name}][{answer.status_code}]: {answer.text}')
        return


    def solve_request(self):
        while True:
            if not self.request_queue.empty():
                #print("\n=============================\n")
                _, client_name, client_request, event_wait = self.request_queue.get(0)
                self.log(f'Executing request {client_name}: {client_request}')
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
                    #print(f"Encaminhando {client_request} para {replicator.name}")
                    replicators_request.append(Process(target=self.make_request,
                        args=(replicator, client_name, client_request['data'], client_request['type'])))
                for rq in replicators_request:
                    rq.start()
                for rq in replicators_request:
                    rq.join()

                event_wait.set()






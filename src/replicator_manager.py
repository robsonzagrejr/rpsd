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
        # Replicators
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

        # Variables
        #self.request_queue = Queue()
        self.manager = Manager()
        self.request_queue = self.manager.list()
        self.request_answer = self.manager.dict()

        # URL
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
        self.log(f"[RECIVE][REQUEST][{data['send_id']}][{data['request']['type'].upper()}]: {data['request']['data']}")
        #self.request_queue.put(
        self.request_queue.append(
            (
                data['timestamp'],
                data['send_id'],
                data['request'],
                event_wait
            )
        )
        request_answer_key = (data['send_id'], data['timestamp'])
        event_wait.wait()
        answer = self.request_answer[request_answer_key]
        return answer[0], answer[1]


    def make_request(self, replicator, client_name, data, rq_type, request_answer_key):
        data['send_id'] = self.name
        self.log(f'[SEND][REQUEST][{replicator.name}]: from {client_name} > {data}')
        answer = requests.post(
                f'http://{replicator.ip}:{replicator.port}/{rq_type}_file',
                json=data
        ) 
        self.log(f'[RECIVE][RESPONSE][{replicator.name}][{answer.status_code}]: {answer.text}')
        if answer.status_code != 200:
            self.request_answer[request_answer_key] = (answer.text, answer.status_code)
        return


    def solve_request(self):
        while True:
            #if not self.request_queue.empty():
            if self.request_queue:
                # Sort requests by timestamp
                self.request_queue.sort()

                # Picking request
                client_timestamp, client_name, client_request, event_wait = self.request_queue.pop(0)
                self.log(f'[EXECUTE][({client_timestamp},{client_name})]: {client_request}')
                client_request['data']['send_id'] = client_name

                if client_request['type'] == 'create':
                    answer = self.create_file(data=client_request['data'])
                elif client_request['type'] == 'update':
                    answer = self.update_file(data=client_request['data'])
                elif client_request['type'] == 'append':
                    answer = self.append_file(data=client_request['data'])
                elif client_request['type'] == 'delete':
                    answer = self.delete_file(data=client_request['data'])
                elif client_request['type'] == 'get':
                    answer = self.get_file(data=client_request['data'])
                request_answer_key = (client_name, client_timestamp)
                self.request_answer[request_answer_key] = answer

                # If an Error occurs
                if answer[1] != 200:
                    event_wait.set()
                    continue

                # Send request to relicators
                replicators_request = []
                for replicator in self.replicators: 
                    #print(f"Encaminhando {client_request} para {replicator.name}")
                    replicators_request.append(
                        Process(
                            target=self.make_request,
                            args=(
                                replicator,
                                client_name,
                                client_request['data'], 
                                client_request['type'],
                                request_answer_key,
                            )
                        )
                    )
                for rq in replicators_request:
                    rq.start()

                # Waiting for replicators
                for rq in replicators_request:
                    rq.join()

                event_wait.set()
                continue


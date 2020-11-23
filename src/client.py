import time
import os
from datetime import datetime
import random
import requests
from multiprocessing import Process, Event

class Client(Process):

    def __init__(self, id, name, ip_replicator_manager, log_server_path, log_server_lock, run_type='simple'):
        super().__init__(name=name)
        self.id = id
        self.name = name
        self.ip_replicator_manager = ip_replicator_manager
        self.run_type = run_type

        # Log
        self.log_path = f'log/{name.lower()}.log'
        os.system(f'rm -rf {self.log_path}')
        with open(self.log_path, 'w+') as log:
            log.write(f'======{self.name} Log======')

        self.log_server_path = log_server_path
        self.log_server_lock = log_server_lock

        #Files
        self.file_names = [
            'file_test_1.txt',
            'file_test_2.txt'
        ]
        return


    def run(self):
        if self.run_type == 'simple':
            self.update_file()
            self.append_file()
        elif self.run_type == 'complex':
            self.create_file()
            self.update_file()
            self.append_file()
            self.get_file()
        return 


    def log(self, text):
        with open(self.log_path, 'a') as log:
            time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
            log.write(f'\n[{self.name}:{time_now}] {text}')

        # Write in general log
        self.log_server_lock.acquire()
        with open(self.log_server_path, 'a') as log:
            time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
            log.write(f'\n[{self.name}:{time_now}] {text}')
        self.log_server_lock.release()
        return


    def mounting_request(self, type_request, file_name, text=None):
        return {
            'send_id':self.name,
            'timestamp':str(time.time()),
            'request': {
                'type': type_request,
                'data': {
                    'file_name': file_name,
                    'text': text
                }
            }
        }


    def create_file(self):
        file_name = self.file_names[self.id%2]
        self.log(f"[REQUEST][CREATE] '{file_name}'")
        answer = requests.post(
                self.ip_replicator_manager,
                json=self.mounting_request('create', file_name, f'Text create by "{self.name}"')
        ) 
        self.log(f'[RESPONSE][CREATE][Replicator_Manager][{answer.status_code}]: {answer.text}')
        return


    def update_file(self):
        file_name = self.file_names[self.id%2]
        text = f'Text update by "{self.name}"'
        self.log(f"[REQUEST][UPDATE] '{text}' > '{file_name}'")
        answer = requests.post(
                self.ip_replicator_manager,
                json=self.mounting_request('update', file_name, text)
        ) 
        self.log(f'[RESPONSE][UPDATE][Replicator_Manager][{answer.status_code}]: {answer.text}')
        return


    def append_file(self):
        file_name = self.file_names[self.id%2]
        text = f'\nText append by "{self.name}"'
        self.log(f"[REQUEST][APPEND] '{text[1:]}' > '{file_name}'")
        answer = requests.post(
                self.ip_replicator_manager,
                json=self.mounting_request('append', file_name, text) 
        ) 
        self.log(f'[RESPONSE][APPEND][Replicator_Manager][{answer.status_code}]: {answer.text}')
        return


    def delete_file(self):
        file_name = self.file_names[self.id%2]
        self.log(f"[REQUEST][DELETE] '{file_name}'")
        answer = requests.post(
                self.ip_replicator_manager,
                json=self.mounting_request('delete', file_name) 
        ) 
        self.log(f'[RESPONSE][DELETE][Replicator_Manager][{answer.status_code}]: {answer.text}')
        return


    def get_file(self):
        file_name = self.file_names[self.id%2]
        self.log(f"[REQUEST][GET] '{file_name}'")
        answer = requests.post(
                self.ip_replicator_manager,
                json=self.mounting_request('get', file_name) 
        ) 
        self.log(f'[RESPONSE][GET][Replicator_Manager][{answer.status_code}]: {answer.text}')
        return

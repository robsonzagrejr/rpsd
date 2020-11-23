import time
import os
from datetime import datetime
import random
import requests
from multiprocessing import Process, Event

class Client(Process):

    def __init__(self, name, ip_replicator_manager, log_server_path, log_server_lock):
        super().__init__(name=name)
        self.name = name
        self.ip_replicator_manager = ip_replicator_manager
        self.log_path = f'log/{name.lower()}.log'
        os.system(f'rm -rf {self.log_path}')

        self.log_server_path = log_server_path
        self.log_server_lock = log_server_lock
        return


    def run(self):
        self.update_file()
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


    def mounting_request(self, type_request, file_name, text):
        return {
            'timestamp':str(time.time()),
            'request': {
                'send_id':self.name,
                'type': type_request,
                'data': {
                    'file_name': file_name,
                    'text': text
                }
            }
        }


    def update_file(self):
        sleep_time = (random.random()*100) % 3
        time.sleep(sleep_time)
        self.log('Making a request to update file')
        response = requests.post(
                self.ip_replicator_manager,
                json=self.mounting_request('update', f'file_test.txt', f'Text update by {self.name} Client')
        ) 
        self.log('Recive answer from replicator manager')
        return


    def append_file(self):
        #sleep_time = (random.random()*100) % 3
        #time.sleep(sleep_time)
        response = requests.post(
                self.ip_replicator_manager,
                json=self.mounting_request('update', f'file_test.txt', f'\nText append by {self.name} Client')
        ) 
        print("\n--------------------")
        print("file_test.txt appended by {self.name}")
        return



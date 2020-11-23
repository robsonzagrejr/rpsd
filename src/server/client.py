import time
import random
from multiprocessing import Process, Event

class Client(Process):

    def __init__(self, name, ip_replicator_manager):
        super().__init__(self, name=name)
        self.ip_replicator_manager = ip_replicator_manager
        return


    def run(self):
        return 


    def mounting_request(self, type_request, file_name, text):
        return {
            'timestamp':str(time.time()),
            'request': {
                'type': type_request,
                'data': {
                    'file_name': file_name,
                    'text': text #f'This is a update of file {self.name}'
                }
            }
        }


    def update_file(self):
        #sleep_time = (random.random()*100) % 3
        #time.sleep(sleep_time)
        response = requests.post(
                IP,
                json=self.mounting_request('update', f'file_test.txt', f'Text update by {self.name} Client')
        ) 
        print("\n+++++++++++++++++++++++++")
        print("file_test.txt updated by {self.name}")
        return


    def append_file(self):
        #sleep_time = (random.random()*100) % 3
        #time.sleep(sleep_time)
        response = requests.post(
                IP,
                json=self.mounting_request('update', f'file_test.txt', f'\nText append by {self.name} Client')
        ) 
        print("\n--------------------")
        print("file_test.txt appended by {self.name}")
        return



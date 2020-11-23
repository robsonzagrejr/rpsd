import time
import random
from multiprocessing import Process

class Client(Process):

    def __init__(self, name, p_replicator):
        Process.__init__(self, name=name)
        self.p_replicator = p_replicator


    def run_kaka(self):
        print(f"I'm alive {self.name}")
        sleep_time = (random.random()*100) % 3
        print(f"{self.name} sleeping for {sleep_time}")
        time.sleep(sleep_time)
        print(f"{self.name} awaked")
        return 


    def update_file(self, file_name, text):
        print('Updating file')
        p_replicator.update_file(file_name, text)
        print('File updated')

        return

    def test_manager(number):
        global type_f
        sleep_time = (random.random()*100) % 3
        print(f'Sleeping {number} {sleep_time}')
        time.sleep(sleep_time)
        response = requests.post(
                IP,
                #json={'number':number, 'timestamp':datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f')}
                json={
                    'timestamp':str(datetime.now()),
                    'request': {
                        'type': 'update',
                        'data': {
                            'file_name': f'file_{number}.txt',
                            'text': f'This is a update of file {number}'
                        }
                    }
                }
        )
        return



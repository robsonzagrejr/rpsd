import time
import random
import os
from multiprocessing import Process

class Replicator(Process):

    def __init__(self):
        super.__init__(self)
        self.backup_path = f'filesystem/backup_{self.name.lower()}'
        os.system(f'rm -rf {self.backup_path}')
        os.system('mkdir -p {self.backup_path}')
        print(f'Created {self.backup_path}')


    def run(self):
        print(f"I'm alive {self.name}")
        sleep_time = (random.random()*100) % 3
        print(f"{self.name} sleeping for {sleep_time}")
        time.sleep(sleep_time)
        print(f"{self.name} awaked")
        return 


    def create_file(self, file_name, text, update=False):
        file_path = f'{self.backup_path}/{file_name}'
        if not update:
            #TODO Check if file exists returning Error
            pass
        else:
            os.system('rm -rf {file_path}')

        with f as open(file_path, 'w+'):
            f.write(text)

        #TODO freeaway father

        return


    def update_file(self, file_name, text):
        print('Upadating file')
        self.create_file(file_name, text, update=True)
        print('File updated')
        return

    def append_file(self, file_name, text):
        print('Appending file')
        #TODO append in file
        print('File appended')
        print('Return to father')
        
        return

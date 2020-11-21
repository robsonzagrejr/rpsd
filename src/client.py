import time
import random
from multiprocessing import Process

class Client(Process):

    def run(self):
        print(f"I'm alive {self.name}")
        sleep_time = (random.random()*100) % 3
        print(f"{self.name} sleeping for {sleep_time}")
        time.sleep(sleep_time)
        print(f"{self.name} awaked")
        return 

import requests
import time
from datetime import datetime
import random
import json
from multiprocessing import Pool
IP = "http://0.0.0.0:8000/"

type_f = 'update'
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


def test_manager_u(number):
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
                    'type': 'append',
                    'data': {
                        'file_name': f'file_{number}.txt',
                        'text': f'This is a update of file {number}'
                    }
                }
            }
    )
    return

pool = Pool(processes=10)
t = time.time()
pool.map(test_manager, range(10))
print("********************")
print(time.time() - t)

pool.map(test_manager_u, range(10))


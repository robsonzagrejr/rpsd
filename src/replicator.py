from multiprocessing import Process
from flask import Flask, Response, request
#from flask_restful import Api, Resource, reqparse
from pathlib import Path
import __main__

import os
import json
from datetime import datetime

class EndpointAction(object):

    def __init__(self, action):
        self.action = action

    def __call__(self, *args):
        # Perform the action
        answer, status = self.action()
        return Response(answer, status=status)



class Replicator(Process):

    def __init__(self, name, ip, port, log_server_path, log_server_lock, server=True):
        Process.__init__(self, name=name)

        # File System
        self.backup_path = f'filesystem/backup_{self.name.lower()}'
        os.system(f'rm -rf {self.backup_path}')
        os.system(f'mkdir -p {self.backup_path}')

        # Log
        self.log_path = f'log/{self.name.lower()}.log'
        os.system(f'rm -rf {self.log_path}')
        with open(self.log_path, 'w+') as log:
            log.write(f'======{self.name} Log======')

        self.log_server_path = log_server_path
        self.log_server_lock = log_server_lock
 
        # Server definitions
        self.app = Flask(name)
        self.name = name
        self.ip = ip
        self.port = port

        # Routes
        if server:
            self.add_endpoint(endpoint='/', handler=self.hello_world)
            #self.add_endpoint(endpoint='/data', handler=self.data, methods=['POST'])
            self.add_endpoint(endpoint='/create_file', handler=self.create_file, methods=['POST'])
            self.add_endpoint(endpoint='/update_file', handler=self.update_file, methods=['POST'])
            self.add_endpoint(endpoint='/append_file', handler=self.append_file, methods=['POST'])
            self.add_endpoint(endpoint='/delete_file', handler=self.delete_file, methods=['POST'])
        self.add_endpoint(endpoint='/get_file', handler=self.get_file, methods=['POST'])

        return


    def run(self):
        self.app.run(host=self.ip, port=self.port, debug=False)
        return


    def add_endpoint(self, endpoint=None, handler=None, methods=['GET']):
        self.app.add_url_rule(rule=endpoint, endpoint=endpoint, view_func=EndpointAction(handler),
                              methods=methods)


    def hello_world(self):
        return f'Hello, World! my name is {self.name}', 200


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


    def get_msg(self, msg_type, file_name=None, text=None, key=None):
        msg = {
            'create': (
                f"File '{file_name}' successfuly created :)",
                200
            ),
            'update': (
                f"File '{file_name}' successfuly updated :)",
                200
            ),
            'append': (
                f"Text '{text}' successfuly appended to '{file_name}' :)",
                200
            ),
            'delete': (
                f"File '{file_name}' successfuly deleted :)",
                200
            ),
            'get': (
                f"File '{file_name}' successfuly returned :)",
                200
            ),
            'not_exists': (
                f"File '{file_name}' not exist :X",
                400
            ),
            'exists': (
                f"File '{file_name}' exists :X",
                400
            ),
            'request_key': (
                f"Request need to contain '{key}' in json :X",
                400
            ),
            'request_json': (
                f"Request need to be json :X",
                400
            )
        }
        return msg[msg_type]


    """
    def make_data_return(self, data):
        return json.dumps(
            {
                'name':self.name,
                'data':data
            }
        )
    """


    def check_file_exist(self, file_name):
        main_path = Path(__main__.__file__).parent
        return os.path.exists(f'{main_path}/{file_name}')

    
    def get_data(self, msg='Except json data', keys=['file_name', 'text', 'send_id'], data=None):
        try:
            if not data:
                data = request.get_json()
            if data:
                for k in keys:
                    if k not in data.keys():
                        return self.get_msg('request_key', key=k)
                return data, 200
            
            return self.get_msg('request_json')
        except:
            return self.get_msg('request_json')


    def create_file(self, update=False, data=None):
        request = data is None
        data, status = self.get_data(data=data)
        if status != 200:
            self.log(f'[ERROR][{status}]: {data}')
            return data, status

        if request:
            if not update:
                self.log(f"[RECIVE][REQUEST][{data['send_id']}][CREATE]: {data['file_name']}")
            else:
                self.log(f"[RECIVE][REQUEST][{data['send_id']}][UPDATE]: '{data['text']}' in {data['file_name']}")

        file_name = data['file_name']
        text = data['text']

        file_path = f'{self.backup_path}/{file_name}'
        if not update:
            if self.check_file_exist(file_path):
                msg, status = self.get_msg('exists', file_name=file_name)
                self.log(msg)
                return msg, status

        else:
            os.system('rm -rf {file_path}')

        with open(file_path, 'w+') as f:
            f.write(text)

        msg, status = self.get_msg('create', file_name=file_name)
        if not update:
            self.log(msg)
        return msg, status


    def update_file(self, data=None):
        msg, status = self.create_file(update=True, data=data)
        if status != 200:
            self.log(f'[ERROR][{status}]: {msg}')
            return msg, status

        file_name = msg.split("'")[1]

        msg, status = self.get_msg('update', file_name=file_name)
        self.log(msg)
        return msg, status


    def append_file(self, data=None):
        request = data is None
        data, status = self.get_data(data=data)
        if status != 200:
            self.log(f'[ERROR][{status}]: {data}')
            return data, status
            
        if request:
            self.log(f"[RECIVE][REQUEST][{data['send_id']}][APPEND]: '{data['text']}' in {data['file_name']}")


        file_name = data['file_name']
        text = data['text']

        file_path = f'{self.backup_path}/{file_name}'
        if not self.check_file_exist(file_path):
            msg, status = self.get_msg('not_exists', file_name=file_name)
            self.log(f'[ERROR][{status}]: {msg}')
            return msg, status

        with open(file_path, 'a') as f:
            f.write(text)

        msg, status = self.get_msg('update', file_name=file_name, text=text)
        self.log(msg)
        return msg, status


    def delete_file(self, data=None):
        request = data is None
        data, status = self.get_data(data=data)
        if status != 200:
            self.log(f'[ERROR][{status}]: {data}')
            return data, status

        if request:
            self.log(f"[RECIVE][REQUEST][{data['send_id']}][DELETE]: {data['file_name']}")

        file_name = data['file_name']
        text = data['text']

        file_path = f'{self.backup_path}/{file_name}'
        if not self.check_file_exist(file_path):
            msg, status = self.get_msg('not_exists', file_name=file_name)
            self.log(f'[ERROR][{status}]: {msg}')
            return msg, status

        os.system(f'rm -rf {file_path}')
        msg, status = self.get_msg('delete', file_name=file_name)
        self.log(msg)
        return msg, status


    def get_file(self, data=None):
        request = data is None
        data, status = self.get_data(data=data)
        if status != 200:
            self.log(f'[ERROR][{status}]: {data}')
            return data, status

        if request:
            self.log(f"[RECIVE][REQUEST][{data['send_id']}][GET]: {data['file_name']}")

        file_name = data['file_name']
        text = data['text']

        file_path = f'{self.backup_path}/{file_name}'
        if not self.check_file_exist(file_path):
            msg, status = self.get_msg('not_exists', file_name=file_name)
            self.log(f'[ERROR][{status}]: {msg}')
            return msg, status

        with open(file_path, 'r') as f:
            file_data = f.read()

        msg, status = self.get_msg('get', file_name=file_name)
        self.log(msg)
        return json.dumps(file_data), status


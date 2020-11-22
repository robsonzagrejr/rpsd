from multiprocessing import Process
from flask import Flask, Response, request
#from flask_restful import Api, Resource, reqparse
from pathlib import Path
import __main__

import os
import json

class EndpointAction(object):

    def __init__(self, action):
        self.action = action

    def __call__(self, *args):
        # Perform the action
        answer, status = self.action()
        return Response(answer, status=status)



class Replicator(Process):

    def __init__(self, name, port, server=True):
        Process.__init__(self, name=name)

        # File System
        self.backup_path = f'filesystem/backup_{self.name.lower()}'
        os.system(f'rm -rf {self.backup_path}')
        os.system(f'mkdir -p {self.backup_path}')
 
        # Server definitions
        self.app = Flask(name)
        self.name = name
        self.port = port

        # Routes
        if server:
            self.add_endpoint(endpoint='/', handler=self.hello_world)
            self.add_endpoint(endpoint='/data', handler=self.data, methods=['POST'])
            self.add_endpoint(endpoint='/create_file', handler=self.create_file, methods=['POST'])
            self.add_endpoint(endpoint='/update_file', handler=self.update_file, methods=['POST'])
            self.add_endpoint(endpoint='/append_file', handler=self.append_file, methods=['POST'])
            self.add_endpoint(endpoint='/delete_file', handler=self.delete_file, methods=['POST'])
        self.add_endpoint(endpoint='/get_file', handler=self.get_file, methods=['POST'])

        return


    def run(self):
        self.app.run(host='0.0.0.0', port=self.port, debug=False)
        return


    def add_endpoint(self, endpoint=None, handler=None, methods=['GET']):
        self.app.add_url_rule(rule=endpoint, endpoint=endpoint, view_func=EndpointAction(handler),
                              methods=methods)


    def hello_world(self):
        return f'Hello, World! my name is {self.name}', 200


    def data(self):
        try:
            data = request.get_json()
            return json.dumps(data), 200
        except:
            return f"Replicator {self.name} except json data", 400


    def make_data_return(self, data):
        return json.dumps(
            {
                'name':self.name,
                'data':data
            }
        )

    def check_file_exist(self, file_name):
        main_path = Path(__main__.__file__).parent
        return os.path.exists(f'{main_path}/{file_name}')

    
    def get_data(self, msg='Except json data', keys=['file_name', 'text']):
        try:
            data = request.get_json()
            if data:
                print(keys)
                for k in keys:
                    if k not in data.keys():
                        return self.make_data_return(f"[{self.name}]|Error: Excepted '{k}' keys"), 400
                return data, 200
            
            return self.make_data_return(f"[{self.name}]|Error: {msg}"), 400
        except:
            return self.make_data_return(f"[{self.name}]|Error: {msg}"), 400


    def create_file(self, update=False, data=None):
        if not data:
            data, status = self.get_data()
            if status != 200:
                return data, status

        file_name = data['file_name']
        text = data['text']

        file_path = f'{self.backup_path}/{file_name}'
        if not update:
            if self.check_file_exist(file_path):
                return self.make_data_return(f"[{self.name}]|Error: File '{file_name}' exists :/"), 400
        else:
            os.system('rm -rf {file_path}')

        with open(file_path, 'w+') as f:
            f.write(text)

        return self.make_data_return(f"[{self.name}] File '{file_name}' successfuly created :)"), 200


    def update_file(self, data=None):
        msg, status = self.create_file(update=True, data=data)
        if status == 200:
            file_name = msg.split("'")[1]
            return self.make_data_return(f"[{self.name}] File '{file_name}' successfuly updated :D"), status
        return msg, status


    def append_file(self, data=None):
        if not data:
            data, status = self.get_data()
            if status != 200:
                return data, status

        file_name = data['file_name']
        text = data['text']

        file_path = f'{self.backup_path}/{file_name}'
        if not self.check_file_exist(file_path):
            return self.make_data_return(f"[{self.name}]|Error: File '{file_name}' do not exists :X"), 400

        with open(file_path, 'a') as f:
            f.write(text)

        return self.make_data_return(f"[{self.name}] Text '{text}' successfuly appended in '{file_name}' :)"), 200


    def delete_file(self, data=None):
        if not data:
            data, status = self.get_data()
            if status != 200:
                return data, status

        file_name = data['file_name']
        text = data['text']

        file_path = f'{self.backup_path}/{file_name}'
        if not self.check_file_exist(file_path):
            return self.make_data_return(f"[{self.name}]|Error: File '{file_name}' do not exists :X"), 400

        os.system(f'rm -rf {file_path}')
        return self.make_data_return(f"[{self.name}] File '{file_name}' successfuly deleted :)"), 200


    def get_file(self, data=None):
        if not data:
            data, status = self.get_data()
            if status != 200:
                return data, status

        file_name = data['file_name']
        text = data['text']

        file_path = f'{self.backup_path}/{file_name}'
        if not self.check_file_exist(file_path):
            return self.make_data_return(f"[{self.name}]|Error: File '{file_name}' do not exists :X"), 400

        with open(file_path, 'r') as f:
            file_data = f.read()

        return self.make_data_return(file_data), 200


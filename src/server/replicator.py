from multiprocessing import Process
from flask import Flask, Response, request
#from flask_restful import Api, Resource, reqparse
import os
import json

class EndpointAction(object):

    def __init__(self, action):
        self.action = action

    def __call__(self, *args):
        # Perform the action
        answer = self.action()

        # Create the answer (budle it in a correctly formatted HTTP answer)
        self.response = Response(answer, status=200, headers={})

        # Send it
        return self.response


class Replicator(Process):

    def __init__(self, name, port, primary=False):
        Process.__init__(self, name=name)

        # File System
        self.backup_path = f'filesystem/backup_{self.name.lower()}'
        os.system(f'rm -rf {self.backup_path}')
        os.system(f'mkdir -p {self.backup_path}')
 
        # Server definitions
        self.app = Flask(name)
        self.name = name
        self.port = port

        # Home route
        self.add_endpoint(endpoint='/', endpoint_name='/',
            handler=self.hello_world)


        self.add_endpoint(endpoint='/data', endpoint_name='/data',
            handler=self.data, methods=['POST'])
        #s1 = SimpleModel(self)
        #self.api = Api(self.app)
        #self.api.add_resource(s1, '/', methods=['GET'])
        return


    def run(self):
        self.app.run(host='0.0.0.0', port=self.port, debug=True)
        return


    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=['GET']):
       self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler),
               methods=methods)


    def hello_world(self):
        return f'Hello, World! my name is {self.name}'


    def data(self):
        try:
            data = request.get_json()
            return json.dumps(data)
        except:
            return f"Replicator {self.name} except json data"


    """
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
    """


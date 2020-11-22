from multiprocessing import Process
from flask import Flask, Response


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

    def __init__(self, name, port):
        Process.__init__(self, name=name)
        self.app = Flask(name)
        self.name = name
        self.port = port
        self.add_endpoint(endpoint='/', endpoint_name='/',
                handler=self.hello_world)

    def run(self):
        self.app.run(host='0.0.0.0', port=self.port, debug=False)
        return

    def hello_world(self):
        return f'Hello, World! my name is {self.name}'

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))


"""
class Replicator(Process):
    app = Flask(__name__)

    def __init__(self, name, port):
        Process.__init__(self, name=name)
        self.name = name
        self.port = port

    def run(self):
        self.app.run(host='0.0.0.0', port=self.port, debug=True)
        return

    @app.route('/')
    def hello_world():
        return f'Hello, World! my name is {name}'

"""

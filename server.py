from flask import Flask,request
from multiprocessing import Process,Queue
import logging
import os
import signal
app = Flask(__name__)

# Development Mode
logging.basicConfig(level=logging.DEBUG)

# Global datastructures - lifetime of the server
pid_table = {}

class Container(object):
    def __init__(self, data):
        self.data = data # Making it generic so that it can be reused for any IPC
    def getData(self):
        return self.data

def generateComponent(comp, q):
    q.put(Container(str(os.getpid())))
    # TODO : Code for component generation
    logging.debug("Component generated")

@app.route('/')
def healthCheck():
    return "I am Up!"

@app.route('/submit', methods=['POST'])
def componentSubmit():
    queue = Queue()
    content = request.get_json()
    logging.debug("Got request : " + str(content))
    p = Process(target=generateComponent, args=(content,queue,))
    p.start()
    child_pid = queue.get()
    pid_table[content['component']['name']] = int(child_pid.getData())
    # TODO : Remove process join after logic.
    p.join()
    return "Success"

@app.route('/component/delete/<name>')
def deleteComponent(name):
    print pid_table
    pid = pid_table[name]
    os.kill(pid, signal.SIGQUIT)
    logging.debug("Component with PID " + str(pid) + " and name " + str(name) + " is removed from the Orchestra")

if __name__ == "__main__":
    app.run()

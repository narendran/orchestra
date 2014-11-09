from flask import Flask,request
from multiprocessing import Process,Queue
import logging
import os
import signal
import redis
import pymongo
import json
app = Flask(__name__)

client = pymongo.MongoClient()
db = client.orchestra

# Development Mode
logging.basicConfig(level=logging.DEBUG)

# Global datastructures - lifetime of the server
pid_table = {}

from datetime import timedelta, datetime
from flask import make_response, request, current_app
from functools import update_wrapper


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

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

def componentSubmitHelper():
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

@app.route('/submitModule', methods=['POST'])
def moduleSubmit():
    print "Reached submitModule"
    content = request.form["modulespec"]
    print content
    jsonFormat = json.loads(content)
    print jsonFormat
    db.modules.insert(jsonFormat)
    return "Success"

@app.route('/submitComponent', methods=['POST'])
def componentSubmit():
    print "Reached submitComponent"
    content = request.form["componentspec"]
    print content
    jsonFormat = json.loads(content)
    print jsonFormat
    db.components.insert(jsonFormat)
    return "Success"

@app.route('/getComponents')
@crossdomain(origin='*')
def getComponent():
    start = datetime.now() 
    cursor = db.components.find()
    print datetime.now() - start
    response = []
    start = datetime.now()
    for doc in cursor:
        response.append(doc)
    print datetime.now() - start
    return str(response)

@app.route('/getModules')
@crossdomain(origin='*')
def getModules():
    start = datetime.now()
    cursor = db.modules.find()
    print datetime.now() - start
    response = []
    start = datetime.now()
    for doc in cursor:
        response.append(doc)
    print datetime.now() - start
    return str(response)

if __name__ == "__main__":
    app.run()

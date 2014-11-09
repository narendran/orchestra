#!/usr/bin/python

import fileinput
import glob
import json
import sys

modulehub = {}


def addModule(module):
    modulehub[module['name']] = module


def getModule(mname):
    return modulehub[mname]


def expand_component(jsontext):
    component = json.loads(jsontext)
    output_python = []

    output_python.append('import redis')
    output_python.append('import json')
    output_python.append("r = redis.StrictRedis(host='localhost', db=0)")
    output_python.append("s = redis.StrictRedis(port=6380, host='localhost', db=0)")
    output_python.append("p = r.pubsub(ignore_subscribe_messages=True)")
    output_python.append("sources = []")

    for source in component['sources']:
        output_python.append("p.subscribe('%s')" % (source))
        output_python.append("sources.append('%s')" % (source))

    # Add component filtering

    module = getModule(component['module']['name'])

    for line in module['logic']['initialization']:
        output_python.append(line)

    # Handling constants/threshold mentioned in the component's spec
    output_python.append("constants = []")
    output_python.append("field = []")
    for line in component['module']['params']:
        if not ":" in line:
            output_python.append("constants.append('%s')" % (line))
        else:
            output_python.append("field.append('"+line.split(':')[1]+"')")
    output_python.append("params = [0] * (len(sources) + len(constants))")

    # From this point on, we handle processing every new tuple
    output_python.append("")
    output_python.append("for m in p.listen():")
    # Ignore non-"message" messages
    output_python.append("  if m is None or m['type'] not in ('message', 'pmessage'):")
    output_python.append("    continue")
    output_python.append("")
    output_python.append("  data = json.loads(m['data'])")
    output_python.append("  p_index = sources.index(str(m['channel']))")
    output_python.append("  params[p_index] = float(data[field[p_index]])")

    output_python.append("  for i,line in enumerate(constants):")
    output_python.append("    params[len(field)+i] = float(line)")
    # Check if all the params are set, and only then proceed to module
    output_python.append("  if all(p is not None for p in params):")
    for line in module['logic']['iteration']:
        output_python.append("    " + line)

    for line in module['logic']['output']:
        output_python.append("    s.publish('" + component['publish'] + "', " + line + ')')
        output_python.append("    print '" + component['publish'] + "', " + line + '')
    output_python.append("    params = [None] * (len(sources) + len(constants))")

    return '\n'.join(output_python)


def main():
    for moduleLoc in glob.glob('modules/*.json'):
        ravg = open(moduleLoc, 'r')
        addModule(json.loads('\n'.join(ravg.readlines())))

    f = open(sys.argv[1], 'r')
    print expand_component('\n'.join(f.readlines()))


if __name__ == "__main__":
    main()

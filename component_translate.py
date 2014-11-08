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
    output_python.append("p = r.pubsub()")

    for source in component['sources']:
        output_python.append("p.subscribe('%s')" % (source))

    # Add component filtering

    module = getModule(component['module']['name'])

    for line in module['logic']['initialization']:
        output_python.append(line)

    # From this point on, we handle processing every new tuple
    output_python.append("")
    output_python.append("while True:")
    output_python.append("  m = p.get_message()")

    # Ignore non-"message" messages
    output_python.append("  if m is None or m['type'] not in ('message', 'pmessage'):")
    output_python.append("    continue")
    output_python.append("")
    # output_python.append("  print m")
    output_python.append("  data = json.loads(m['data'])")

    # Set up parameters for module iteration
    output_python.append("  params = []")
    i = 0
    for line in component['module']['params']:
        output_python.append("  params.append(float(data['%s']))" % (line))
        i = i + 1

    for line in module['logic']['iteration']:
        output_python.append("  " + line)

    for line in module['logic']['output']:
        output_python.append("  r.publish('" + component['publish'] + "', " + line + ')')
        output_python.append("  print '" + component['publish'] + "', " + line + '')

    return '\n'.join(output_python)


def main():
    for moduleLoc in glob.glob('modules/*.json'):
        ravg = open(moduleLoc, 'r')
        addModule(json.loads('\n'.join(ravg.readlines())))

    f = open(sys.argv[1], 'r')
    print expand_component('\n'.join(f.readlines()))


if __name__ == "__main__":
    main()

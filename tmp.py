import config
import redis
import json
r = redis.StrictRedis(host=config.RAW_QUEUE_HOST, port=config.RAW_QUEUE_PORT, db=0)
s = redis.StrictRedis(host=config.PROCESSED_QUEUE_HOST, port=config.PROCESSED_QUEUE_PORT, db=0)
p = r.pubsub(ignore_subscribe_messages=True)
sources = []
p.subscribe('myo_sensor')
sources.append('myo_sensor')
p.subscribe('myo_sensor')
sources.append('myo_sensor')
conjunction = 0
constants = []
field = []
field.append('x')
constants.append('-0.25')
constants.append('0.05')
field.append('y')
constants.append('0.1')
constants.append('0.6')
params = [0] * (len(sources) + len(constants))

for m in p.listen():
  if m is None or m['type'] not in ('message', 'pmessage'):
    continue

  data = json.loads(m['data'])
  indices = [i for i, x in enumerate(sources) if x == str(m['channel'])]
  for p_index in indices:
    params[p_index] = float(data[field[p_index]])
  for i,line in enumerate(constants):
    params[len(field)+i] = float(line)
  if all(p is not None for p in params):
    lower1 = params[2]
    upper1 = params[3]
    lower2 = params[4]
    upper2 = params[5]
    # Ranging params[0] given predicate params[1] is true
    if lower2 <= params[1] <= upper2:
      conjunction = (params[0] - lower1) / (upper1 - lower1)
    else:
      conjunction = -1
    s.publish('volume_control', conjunction)
    print 'volume_control', conjunction
    params = [None] * (len(sources) + len(constants))

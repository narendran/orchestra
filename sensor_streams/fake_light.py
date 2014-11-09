from uuid import getnode as get_mac
import calendar
import time
import redis
import config
import json
import random

""" Reading pin value from Analog port 3
	The resulting x value can be in the range of 3 to 75.
	The sensor readings are real-time, no noticeable delay
"""

r = redis.StrictRedis(host=config.RAW_QUEUE_HOST, port=config.RAW_QUEUE_PORT, db=0)
macaddr = get_mac()
while(1):
	x = random.randint(1, 100)
	data_tuple = {}
	data_tuple['sensor_id'] = str(macaddr)
	data_tuple['ts'] = str(calendar.timegm(time.gmtime()))
	data_tuple['reading'] = str(x)
	r.publish('light_sensor', json.dumps(data_tuple))
	time.sleep(0.5)


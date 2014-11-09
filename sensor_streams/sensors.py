from uuid import getnode as get_mac
import mraa
import time
import redis
import config
import time
import json
import calendar

""" Reading pin value from Analog port 3
	The resulting x value can be in the range of 3 to 75.
	The sensor readings are real-time, no noticeable delay
"""

lightSensor = mraa.Aio(3)
heatSensor = mraa.Aio(2)
touchSensor = mraa.Aio(1)
soundSensor = mraa.Aio(0)

r = redis.StrictRedis(host=config.RAW_QUEUE_HOST, port=config.RAW_QUEUE_PORT, db=0)
macaddr = get_mac()
while(1):
	data_tuple = {}
	data_tuple['sensor_id'] = str(macaddr)
	data_tuple['ts'] = str(calendar.timegm(time.gmtime()))

	data_tuple['reading'] = str(lightSensor.read())
	r.publish('light_sensor', json.dumps(data_tuple))

	data_tuple['reading'] = str(heatSensor.read())
	r.publish('heat_sensor', json.dumps(data_tuple))

	data_tuple['reading'] = str(touchSensor.read())
	r.publish('touch_sensor', json.dumps(data_tuple))

	data_tuple['reading'] = str(soundSensor.read())
	r.publish('sound_sensor', json.dumps(data_tuple))

	time.sleep(0.1)

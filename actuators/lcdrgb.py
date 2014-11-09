#!usr/bin/python

import pyupm_i2clcd as lcd
import time
import redis
import config


r = redis.StrictRedis(host=config.PROCESSED_QUEUE_HOST, port=config.PROCESSED_QUEUE_PORT, db=0)
p = r.pubsub()
p.subscribe('fire_probability')


def flashEmergencyMessage():
    x = lcd.Jhd1313m1(0, 0x3E, 0x62)
    x.clear()
    time.sleep(0.1)
    x.write('Fire Warning!')
    i = 0

    while i < 20:
        x.setColor(255, 0, 0)
        time.sleep(0.1)
        x.setColor(255, 255, 255)
        time.sleep(0.1)
        i = i + 1

    x.clear()
    time.sleep(0.1)
    x.write('Hello, World!')

x = lcd.Jhd1313m1(0, 0x3E, 0x62)
x.clear()
time.sleep(0.1)
x.write('Hello, World!')

for message in p.listen():
    print message['data']
    if message['data'] == str(True):
        flashEmergencyMessage()

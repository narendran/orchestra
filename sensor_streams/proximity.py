#!/usr/bin/env python
from uuid import getnode as get_mac
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import calendar
import cv
import config
import json
import numpy as np
import redis
import time


r = redis.StrictRedis(host=config.RAW_QUEUE_HOST, port=config.RAW_QUEUE_PORT, db=0)
macaddr = get_mac()


def doloop():
    global depth, rgb
    while True:
        # Get a fresh frame
        (rgb, _) = get_video()

        # Get average coloring of a center square across for each of RGB
        _r, g, b = np.mean(np.mean(rgb[220:260, 300:340], axis=0), axis=0)
        print _r, g, b
        data_tuple = {}
        data_tuple['sensor_id'] = str(macaddr)
        data_tuple['ts'] = str(calendar.timegm(time.gmtime()))
        data_tuple['r'] = str(_r)
        data_tuple['g'] = str(g)
        data_tuple['b'] = str(b)
        r.publish('proximity', json.dumps(data_tuple))
        time.sleep(0.1)

doloop()

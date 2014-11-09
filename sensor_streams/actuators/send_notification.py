import requests
import redis
r = redis.StrictRedis(port=6380,host='localhost', db=0)
p = r.pubsub(ignore_subscribe_messages=True)
p.subscribe('fire_probability')

for m in p.listen():
    if m is None or m['type'] not in ('message', 'pmessage'):
        continue
    print m['data']
    if m['data'] == str(True):
        print "TRIGGERED"
        url = "https://api.pushover.net/1/messages.json"
        payload = {'token': 'aJT1pkgrWczt7wcupCZg6YvKhckxs3', 'user': 'u2kuonYSsJvky7CPQaZR8gNL51ZGPR','message': 'There is a potential fire at your place in San Francisco'} 
        r = requests.post(url, data=payload)
        print r

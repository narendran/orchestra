import sendgrid
import redis
r = redis.StrictRedis(port=6380, host='localhost', db=0)
p = r.pubsub(ignore_subscribe_messages=True)
p.subscribe('sound_detection_results')

sg = sendgrid.SendGridClient('narendran1890', 'naren1890')

message = sendgrid.Mail()
message.add_to('Narendran <narendran.thangarajan@gmail.com>')
message.set_subject('[IOT ALERT] Sound detected!')
message.set_html('Suspicious sound detected!')
message.set_text('Auto alert!')
message.set_from('Your IoT guard <naren@eng.ucsd.com>')

for m in p.listen():
  if m is None or m['type'] not in ('message', 'pmessage'):
    continue
  print m['data']
  if m['data'] == str(True):
    status, msg = sg.send(message)

import Leap, sys 
from uuid import getnode as get_mac
import time
import redis
import config
import json

r = redis.StrictRedis(host=config.RAW_QUEUE_HOST, port=config.RAW_QUEUE_PORT    , db=0)
macaddr =  get_mac()
current_milli_time = lambda: int(round(time.time() * 1000))

class OrchestraListener(Leap.Listener):

    def on_init(self, controller):
        self.prev_ts = 0;
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_disconnect(self, controller):
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Smoothening for handling load
        ts = current_milli_time()
        if ( ts - self.prev_ts < 100) :
            return
        frame = controller.frame()
        for hand in frame.hands:
            if hand.is_left:
                return
            arm = hand.arm
            print " wrist position:" + str(arm.wrist_position.x) + " , " + str(arm.wrist_position.y) + " , " + str(arm.wrist_position.z)
            data_tuple = {}
            data_tuple['sensor_id'] = str(macaddr)
            data_tuple['ts'] = str(ts)
            data_tuple['reading_x'] = str(arm.wrist_position.x)
            data_tuple['reading_y'] = str(arm.wrist_position.y)
            data_tuple['reading_z'] = str(arm.wrist_position.z)
            self.prev_ts = ts
            print data_tuple
            r.publish('leap_motion_sensor', json.dumps(data_tuple))

def main():
    listener = OrchestraListener()
    controller = Leap.Controller()
    controller.add_listener(listener)

    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        controller.remove_listener(listener)

if __name__ == "__main__":
    main()


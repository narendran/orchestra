var redis = require("redis"), client = redis.createClient(7000, "10.120.115.27")Myo = require('myo')
var myMyo = Myo.create();
prev_ts = 0
myMyo.on('orientation', function(data){
    var ts = (new Date).getTime();
    if ( ts - prev_ts < 100 ) { return }
    console.log(data);
    data_tuple = {}
    data_tuple.sensor_id = 
    data_tuple.ts = ts.toString();
    data_tuple.x = data.x.toString();
    data_tuple.y = data.y.toString();
    data_tuple.z = data.z.toString();
    data_tuple.w = data.w.toString();
    client.publish("myo_sensor", JSON.stringify(data_tuple));
});

# Not going to pursue this since the Grove temperature doesn't seem to work
import pyupm_grove as grove
x = grove.GroveTemp(0)
print x.value()

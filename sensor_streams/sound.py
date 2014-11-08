#Not pursuing since the UPM library doesnt support this
import pyupm_mic
import numpy as np

mymic = pyupm_mic.Microphone(0)
#x = pyupm_mic.uint16Array(3)
#x = [uint16(10)] * 10
x = np.arange(3, dtype=np.uint16)
mymic.getSampledWindow(100, 3, x)

from devices.Accelerometer import Accelerometer
from util.config import Config
from time import sleep
config = Config()
acc = Accelerometer(config)
while True:
    acc.GetCalcReport()
    sleep(0.5)


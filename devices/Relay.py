from gpiozero import LED
from time import sleep

class Relay:
    def __init__(self, config):
        self.pin_to_circuit = config.Relay_GPIO_pin
        self.relay = LED(self.pin_to_circuit, active_high=False, initial_value=False)


    def on(self):
        self.relay.on()

    def off(self):
        self.relay.off()

def waitfor(command, timeout):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    import subprocess, datetime, os, time, signal
    start = datetime.datetime.now()
    process = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        time.sleep(0.2)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return None
    return process.stdout.readlines()


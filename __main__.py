"""Manage Bosch laser ranger and hardware to obtain bearing, 3D orientation, location, time,
provide a display and interface, report UPS status"""

import logging
from util.config import Args, Config
from util.logging import LaserLog
from _version import __version__
from devices.ScreenAndButtons import ScreenAndButtons
from devices.Relay import Relay
from devices.Rotary import Rotary
from devices.Accelerometer import Accelerometer
from devices.UPS import UPS
from os.path import exists
import subprocess
import datetime, os, time, signal

logger = logging.getLogger(__name__)

DEBUG = True


def waitfor(command, timeout):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    start = datetime.datetime.now()
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    while process.poll() is None:
        time.sleep(0.2)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return None
    return process.stdout.readlines()


def bosch_usb_drive_off(relay):
    path = "/media/jlovell/GLM400CL"
    if exists(path):
        command = "umount {}".format(path)
        waitfor(command, 15)
        relay.off()
    else:
        return False


def bosch_usb_drive_on(relay):
    relay.on()
    time.sleep(5)
    path = "/media/jlovell/GLM400CL"
    if not exists(path):
        print("No drive drive found")
        return False
    else:
        print("Drive mounted")
        return True


def wait_for_button():
    pass


def get_rotary():
    pass


def get_accelerometer_orientation():
    pass


def show_orientation_data():
    pass


def check_for_usb_drive():
    pass


def mount_usb_drive():
    pass


def get_bosch_data():
    pass


def show_bosch_data():
    pass


def show_status():
    pass


def main():
    """Initialise and start the loop"""
    # Read command-line arguments, config from the config file and env variables
    config_in = Args()
    # --------------------------------------------------------------------------
    # Create a configuration instance and add the parameters from above
    # Config instance
    config = Config()
    # Load in the config
    config.load(config_in)
    # check the config makes sense
    config.check_config()
    # --------------------------------------------------------------------------
    # Set up logging
    level = logging.INFO
    if DEBUG:
        level = logging.DEBUG
    LaserLog(
        config.LogDir,
        "LaserRangefinder.log",
        level=level,
    )
    logger.info("LaserRangefinder version {}".format(__version__))
    # --------------------------------------------------------------------------
    # Initialise hardware
    # Screen, then start showing status info
    screen = ScreenAndButtons()
    # Relay
    relay = Relay(config)
    # Rotary Encoder
    rotary = Rotary(config)
    # Accelerometer
    accelerometer = Accelerometer(config)
    # UPS
    ups = UPS(config)
    # GPS (skip for now)

    # --------------------------------------------------------------------------
    # Initialise data arrays

    # --------------------------------------------------------------------------
    # Dismount Bosh USB drive and turn off 5V
    bosch_usb_drive_off()

    # --------------------------------------------------------------------------
    # Start the loop
    while True:
        # wait for a button press
        key = wait_for_button()
        if key == 1:
            # button 1 pressed
            # Measurement
            rotary_angle = get_rotary()
            accelerometer_orientation = get_accelerometer_orientation()
            # gps_data = get_GPS()
            # Show data on screen
            show_orientation_data()
        elif key == 2:
            # button 2 pressed
            # Finished. Get data
            # Turn on 5V to Bosch
            bosch_usb_drive_on()
            # Mount USB drive (or check that it is mounted)
            if not check_for_usb_drive():
                mount_usb_drive()
            # get data from drive
            bosch_data = get_bosch_data()
            # show orientation and bosch data on screen
            show_orientation_data()
            show_bosch_data()
        else:
            # button 3 pressed
            # Show status
            show_status()


if __name__ == "__main__":
    main()

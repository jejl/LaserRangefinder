"""Manage Bosch laser ranger and hardware to obtain bearing, 3D orientation, location, time,
provide a display and interface, report UPS status"""

import logging
from util.config import Args, Config
from _version import __version__

logger = logging.getLogger(__name__)

DEBUG = True

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
    if config.monit:
        level = logging.CRITICAL
    if DEBUG:
        level = logging.DEBUG
    quiet = config.quiet or config.monit
    FeshLog(
        config.LogDir,
        "fesh3.log",
        quiet=quiet,
        level=level,
    )
    logger.info("Fesh3 version {}".format(__version__))

if __name__ == "__main__":
    main()

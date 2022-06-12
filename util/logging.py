"""Logging configuration for LaserRangefinder"""
import logging
import logging.config
import logging.handlers
from pythonjsonlogger import jsonlogger

logger = logging.getLogger(__name__)


class LaserLog:
    def __init__(
        self, log_dir: str, log_filename: str, level=logging.INFO
    ):
        """Setup logging parameters

        Parameters
        ----------
        log_dir
            Directory to put the log file
        log_filename
            Name of the log file in log_filename
        level
            logging level
        """
        log_file_str = "{}/{}".format(log_dir, log_filename)

        LOGGING_CONFIG = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {  # The formatter name, it can be anything that I wish
                    "format": "%(asctime)s:%(name)s:%(process)d:%(lineno)d "
                    "%(levelname)s %(message)s",
                    # What to add in the message
                    "datefmt": "%Y-%m-%d %H:%M:%S",  # How to display dates
                },
                "simple": {  # The formatter name
                    "format": "%(message)s",  # As simple as possible!
                },
                "simple_with_time": {  # The formatter name
                    "format": "%(asctime)s %(message)s",  # As simple as possible, with time tag
                    "datefmt": "%H:%M:%S",  # How to display dates
                },
                "json": {  # The formatter name
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    # The class to instantiate!
                    # Json is more complex, but easier to read, display all attributes!
                    "format": """
                            asctime: %(asctime)s
                            created: %(created)f
                            filename: %(filename)s
                            funcName: %(funcName)s
                            levelname: %(levelname)s
                            levelno: %(levelno)s
                            lineno: %(lineno)d
                            message: %(message)s
                            module: %(module)s
                            msec: %(msecs)d
                            name: %(name)s
                            pathname: %(pathname)s
                            process: %(process)d
                            processName: %(processName)s
                            relativeCreated: %(relativeCreated)d
                            thread: %(thread)d
                            threadName: %(threadName)s
                            exc_info: %(exc_info)s
                        """,
                    "datefmt": "%Y-%m-%d %H:%M:%S",  # How to display dates
                },
            },
            "handlers": {
                "logfile": {  # The handler name
                    "formatter": "default",  # Refer to the formatter defined above
                    "level": level,
                    "class": "logging.handlers.RotatingFileHandler",
                    # OUTPUT: Which class to use
                    "filename": log_file_str,
                    # Param for class above. Defines filename to use, load it from constant
                    "backupCount": 2,
                    # Param for class above. Defines how many log files to keep as it grows
                },
                "verbose_output": {  # The handler name
                    "formatter": "simple_with_time",  # Refer to the formatter defined above
                    "level": level,
                    "class": "logging.StreamHandler",  # OUTPUT: Which class to use
                    "stream": "ext://sys.stdout",
                    # Param for class above. It means stream to console
                },
                "json": {  # The handler name
                    "formatter": "json",  # Refer to the formatter defined above
                    "class": "logging.StreamHandler",
                    # OUTPUT: Same as above, stream to console
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "LaserRangefinder": {  # The name of the logger, this SHOULD match your module!
                    "level": level,
                    "handlers": [
                        "verbose_output",  # Refer the handler defined above
                    ],
                },
            },
            "root": {  # All loggers
                "level": level,
                "handlers": [
                    "logfile",  # Refer the handler defined above
                    # "verbose_output",  # Refer the handler defined above
                    # "json",  # Refer the handler defined above
                ],
            },
        }

        logging.config.dictConfig(LOGGING_CONFIG)

        logger.info("Writing to log file {}.".format(log_file_str))

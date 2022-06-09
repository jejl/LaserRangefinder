#!/usr/bin/env python3
"""Manage Fesh3 configuration

This code manages configuration parameters for Fesh3, obtained from the command line, environment
variables and config files. Fesh3 will take its configuration in the following priority order
from lowest to highest:

* Two config files, in this order:
    * `/usr2/control/skedf.ctl`
    * `/usr2/control/fesh3.config`
* Environment variables
* Command-line parameters
"""
import datetime
import logging
import re
import string
from collections import OrderedDict
from configparser import ConfigParser, ExtendedInterpolation
from datetime import datetime
from os import path
from typing import Union

import configargparse

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        """Initialise the configuration object and set up default configuration parameters"""

        def _parse_onoff(val: str) -> str:
            """
            Parse a string containing "on" or "off" (case insensitive), return "on" or "off"
            witht the default of "off" if the string is not recognised.

            Parameters
            ----------
            val: "on" or "off", case insensitive

            Returns
            -------
            "on" or "off"
            """
            val = val.lower()
            if val in ["on", "off"]:
                return val
            else:
                return "off"


        # Initialise the configuration object including converters for onoff, contcal and VSI
        # alignment
        self.config = ConfigParser(
            converters={
                "onoff": _parse_onoff,
            }
        )
        # Allows the config file to have extended interpolation. See
        # https://docs.python.org/3.7/library/configparser.html#configparser.ExtendedInterpolation
        self.config._interpolation = ExtendedInterpolation()

        ##### Initialise the configuration object with default values #####
        # parameters found in LaserRangefinder.config:
        self.LogDir = "/home/jlovell/Logs"
        # I2C address of the accelerometer
        self.accel_addr = "0x1D"
        # GPS parameters
        self.GPS_port = "/dev/ttyS0"
        self.GPS_baudrate = 9600
        # Relay pin number (GPIO BCM)
        self.Relay_GPIO_pin = 1
        # Rotary encoder pins (GPIO BCM)
        self.Encoder_GPIO_left_pin = 12
        self.Encoder_GPIO_right_pin = 23

    def load(self, arg: Union[tuple, configargparse.Namespace]):
        """Puts configuration data from config files, command-line and env vars into variables

        Parameter
        ----------
        arg
            if arg is a tuple of length 2 then configargparse:parse_known_args()
            has been called and returned and there may be unprocessed arguments in arg[1].
            arg[0] is a Namespace with all processed arguments while arg[1] contains unprocessed
            parameters that are in the config files but not command-line options

        """

        extra_args = []
        if isinstance(arg.args, tuple):
            args = arg.args[0]
            extra_args = arg.args[1]
        elif isinstance(arg.args, configargparse.Namespace):
            args = arg.args
        else:
            raise RuntimeError(
                "Unknown data type from configargparse (which "
                "interprets command-line, config files and env vars)."
            )

        # ------------------------------------------------------------------------------------------
        # parameters found in LaserRangefinder.config:
        if args.LogDir:
            self.LogDir = args.LogDir.rstrip("/")
        if args.AccelAddr:
            self.accel_addr = args.AccelAddr
        if args.GPSPort:
            self.GPS_port = args.GPSPort


    def check_config(self):
        """Makes checks of configuration parameters and will raise an exception if there's a problem"""
        # Check the configuration
        if not path.exists(self.LogDir):
            raise OSError(
                2,
                "Can't find the directory for the Log file. Check the config file is correct: ",
                self.LogDir,
            )

        if not path.exists(self.GPS_port):
            raise OSError(
                2,
                "Can't find the serial port for the GPS: ",
                self.GPS_port,
            )

    def _get_arg_from_extra_args(
        self, extra_args: list, parameter_name: str
    ) -> Union[str, list]:
        """Given args and a parameter to search for, return the value as str or list of strs

        This is used for filtering results from configargparse, particularly when there are
        parameters not included on the command line

        Parameters
        ----------
        extra_args
            a list of arguments from configargparse. format is e.g. ['--parameter1=value',
            '--parameter2=value2', '--parameter2=value3']. is a parameter name is repeated,
            its values are returned as a list
        parameter_name
            the parameter name to search for
        Returns
        -------
        arg
            a string or list of strings containing the parameter values
            None = none found
        """

        arg = None  # default argument value to return
        if any(
            parameter_name in s for s in extra_args
        ):  # parameter_name is in extra_args
            search_string_indices = [s for s in extra_args if parameter_name in s]
            # value(s) of the parameter
            param_values = [
                word.split("=")[-1:][0].strip(string.whitespace)
                for word in search_string_indices
            ]
            len_indices = len(search_string_indices)
            # returnf a single value if there's only one, otherwise a list of them
            if len_indices == 1:
                arg = param_values[0]
            else:
                arg = param_values
        return arg


class Args:
    """This class uses the Argparse library to process config files and command-line arguments"""

    def __init__(
        self,
        default_config_file="/usr2/control/skedf.ctl",
    ):
        """Set up command-line parameters"""

        # Process the arguments once just so that the --help option produces a sensible output.
        # TODO: There must be a better way.
        help_parser = configargparse.ArgParser()
        help_parser = self.add_skedf_args(help_parser, "", "")
        help_parser = self.add_remaining_args(help_parser, {}, True)
        args_tmp = help_parser.parse_known_args()

        # Now process the arguments for real.

        # first we want to check the command-line params to see if the locations of the skedf and
        # fesh3 config files are correct
        parser_cfg_file_check = configargparse.ArgParser()
        self.add_skedf_args(
            parser_cfg_file_check, default_config_file_skedf, default_config_file_fesh
        )
        (config_file_args, remaining_args) = parser_cfg_file_check.parse_known_args()

        default_config_file_fesh = config_file_args.ConfigFile
        default_config_file_skedf = config_file_args.SkedConfigFile
        # Define a parser for skedf.ctl
        parser_skedf = configargparse.ArgParser(
            default_config_files=[default_config_file_skedf],
            config_file_parser_class=CustomConfigParser,
        )
        # Not setting up any arguments here. Getting args back as a list in args_skedf[1]. Use
        # these as default values below, to be overriden by the fesh config file the command line,
        # env_variables when we run ArgParser
        args_skedf = parser_skedf.parse_known_args()

        items = OrderedDict()
        for keyval in args_skedf[1]:
            if "=" in keyval:
                (k, v) = keyval.split("=", 1)
                # print(k, v)
                items[k[2:]] = v
        # The schedules directory must be defined. Stop here if it's not
        if not "schedules" in items or not items["schedules"]:
            msg = (
                "\nFesh3 requires that $schedules is defined in skedf.ctl.\n"
                "The default of '.' (i.e. the directory the software is\n"
                "started in) is too arbitrary and could cause fesh3 to\n"
                "lose track of files. Fesh3 will not execute unless $schedules\n"
                "is defined. Exiting.\n"
            )
            raise Exception(msg)
        # Also check on other parameters that are used. Set defaults if they weren't set in
        # skedf.ctl. NOTE: These are the defaults that are set in the FS if not defined in skedf.ctl
        # We're just making sure they are preserved here.
        # TODO: This is a bit messy because if
        #  the FS defaults ever change, we have to remember to duplicate the change here
        # TODO: If things are changed here, they also need to be done in add_remaining_args
        if not "misc.tpicd" in items:
            items["misc.tpicd"] = "NO 0"
        if not "misc.vsi_align" in items:
            items["misc.vsi_align"] = "NONE"
        if not "misc.cont_cal" in items:
            items["misc.cont_cal"] = "OFF"
        if not "misc.cont_cal_polarity" in items:
            items["misc.cont_cal_polarity"] = "NONE"
        if not "misc.use_setup_proc" in items:
            items["misc.use_setup_proc"] = "NO"
        if not "misc.vdif_single_thread_per_file" in items:
            items["misc.vdif_single_thread_per_file"] = "IGNORE"

        self.parser = configargparse.ArgParser(
            remaining_args,
            default_config_files=[default_config_file_fesh],
            description=(
                "Automated schedule file preparation for the current, next or specified session.\n\n"
                "A check for the latest version of the Master File(s) is done first, but skipped if the\n"
                "time since the last check is less than a specified amount (configureable on the command\n"
                "line or in the config file). Similarly, checks on schedule files are only done if the\n"
                "time since the last check exceeds a specified time.\nChecks can be forced on the command\n"
                "line."
            ),
        )

        # Now add any arguments not already added to the parser
        self.add_remaining_args(self.parser, items)

        self.args = self.parser.parse_known_args()

    def add_skedf_args(
        self,
        parser_cfg_file_check: configargparse.ArgParser,
        default_config_file_skedf: str,
        default_config_file_fesh: str,
    ):
        """Add just the --ConfigFile and --SkedConfigFile arguments to parser_cfg_file_check

        Parameters
        ----------
        parser_cfg_file_check: ArgParser to add the parameters to
        default_config_file_skedf: The default value for --SkedConfigFile
        default_config_file_fesh: The default value for --ConfigFile

        """
        parser_cfg_file_check.add_argument(
            "-k",
            "--SkedConfigFile",
            is_config_file=True,
            default=default_config_file_skedf,
            help="The location of the skedf.cfg configuration file",
        )
        parser_cfg_file_check.add_argument(
            "-c",
            "--ConfigFile",
            is_config_file=True,
            default=default_config_file_fesh,
            help="The fesh3 configuration file to use. e.g. /usr2/control/fesh3.config",
        )
        return parser_cfg_file_check

    def add_remaining_args(
        self, psr: configargparse.ArgParser, items: dict, no_defaults: bool = False
    ) -> configargparse.ArgParser:
        """Add all the arguments not already added to the parser

        Parameters
        ----------
        psr: ArgParser to add the parameters to
        items: dictionary of parameters to be added
        no_defaults: There are the defaults that are set in the FS if not defined in skedf.ctl.
        If no_defaults is True, these are all set to None.

        Returns
        -------
        psr following modifications
        """
        now = datetime.utcnow()

        if no_defaults:
            # These are the defaults that are set in the FS if not defined in skedf.ctl
            # We're just making sure they are preserved here.
            items["schedules"] = None
            items["proc"] = None
            items["snap"] = None
            items["schedules"] = None
            items["misc.tpicd"] = None
            items["misc.vsi_align"] = None
            items["misc.cont_cal"] = None
            items["misc.cont_cal_polarity"] = None
            items["misc.use_setup_proc"] = None
            items["misc.vdif_single_thread_per_file"] = None

        psr.add_argument(
            "-g",
            "--get",
            default=None,
            help="Just get a schedule for this specified session. Give the name of the session (e.g. r4951).",
        )
        psr.add_argument(
            "-m",
            "--master-update",
            action="store_true",
            default=False,
            help="Force a download of the Master Schedule (default = False), but just on the first check cycle.",
        )

        psr.add_argument(
            "-u",
            "--sched-update",
            action="store_true",
            default=False,
            help="Force a download of the Schedules (default = False), but just on the first check cycle.",
        )

        psr.add_argument(
            "-n",
            "--current",
            "--now",
            action="store_true",
            default=False,
            help="Only process the current or next experiment",
        )

        psr.add_argument(
            "-o",
            "--once",
            action="store_true",
            default=False,
            help="Just run once then exit, don't go into a wait loop (default = False)",
        )

        psr.add_argument(
            "--update",
            action="store_true",
            default=False,
            help="Force an update to the schedule file when there's a new one available to replace the old one. The "
            "default behaviour is to give the new file the name <code>.skd.new and prompt the user to take "
            "action. The file will also be drudged if the DoDrudg option is True",
        )

        psr.add_argument(
            "--SchedDir",
            default=items["schedules"],
            help="Schedule file directory",
        )

        psr.add_argument(
            "--ProcDir",
            default=items["proc"],
            help="Procedure (PRC) file directory",
        )

        psr.add_argument(
            "--SnapDir",
            default=items["snap"],
            help="SNAP file directory",
        )

        psr.add_argument(
            "--LstDir",
            default=items["schedules"],
            help="LST file directory",
            env_var="LIST_DIR",
        )

        psr.add_argument(
            "--LogDir",
            default="/usr2/log",
            help="Log file directory",
        )
        psr.add_argument(
            "--Station",
            nargs="*",
            required=False,
            type=self.station_label,
            help='Station to consider (two letter code, e.g. "mg")',
        )

        psr.add_argument(
            "--StationName",
            nargs="*",
            required=False,
            help='Longer version name of the Station (e.g. "GGAO12M")',
        )
        psr.add_argument(
            "--StationGroup",
            nargs="*",
            required=False,
            help='Station grouping abbreviation (e.g. "NS")',
        )

        psr.add_argument(
            "--EmailNotifications",
            type=self._str2bool,
            const=True,
            default=False,
            nargs="?",
            help="Send notifications by email. The fesh3 config file will be read for details on "
            "mail server, recipients etc",
        )

        psr.add_argument(
            "--GetMaster",
            type=self._str2bool,
            const=True,
            default=True,
            nargs="?",
            help="Maintain a local copy of the main Multi-Agency schedule, i.e. mostly 24h sessions (default = True)",
        )

        psr.add_argument(
            "--GetMasterIntensive",
            type=self._str2bool,
            const=True,
            default=True,
            nargs="?",
            help="Maintain a local copy of the main Multi-Agency Intensive schedule (default = "
            "True)",
        )

        psr.add_argument(
            "--SchedTypes",
            nargs="*",
            default=["skd"],
            help="Schedule file formats to be obtained? This is a prioritised list with the "
            'highest priority first. Use the file name suffix ("vex" and/or "skd") and '
            "comma-separated.",
        )


        psr.add_argument(
            "-l",
            "--LookAheadTimeDays",
            default=None,
            type=float,
            help="Only look for schedules less than this number of days away (default is 7)",
        )

        psr.add_argument(
            "-d",
            "--DoDrudg",
            type=self._str2bool,
            const=True,
            default=True,
            nargs="?",
            help="Run Drudg on the downloaded/updated schedules (default = True)",
        )

        psr.add_argument(
            "--DrudgBinary",
            default="/usr2/fs/bin/drudg",
            help="Location of Drudg executable (default = /usr2/fs/bin/drudg)",
            required=False,
        )

        psr.add_argument(
            "--TpiPeriod",
            default=items["misc.tpicd"],
            env_var="FESH_GEO_TPICD",
            help="Drudg config: TPI period in centiseconds. 0 = don't use the TPI daemon (default)",
        )

        psr.add_argument(
            "--VsiAlign",
            default=items["misc.vsi_align"],
            env_var="FESH_GEO_VSI_ALIGN",
            help="Drudg config: Applicable only for PFB DBBCs,\nnone = never use dbbc=vsi_align=... (default)\n0 = "
            "always use dbbc=vsi_align=0\n1 = always use dbbc=vsi_align=1",
        )

        psr.add_argument(
            "--ContCalAction",
            default=items["misc.cont_cal"],
            env_var="FESH_GEO_CONT_CAL",
            help="Drudg config: Continuous cal option. Either 'on' or 'off'. Default is 'off'",
        )
        #  3. If continuous cal is in use, what is the polarity? Options are 0-3 or "none". Default is none
        # ContCalPolarity = none
        psr.add_argument(
            "--ContCalPolarity",
            default=items["misc.cont_cal_polarity"],
            env_var="FESH_GEO_CONT_CAL_POLARITY",
            help="Drudg config: If continuous cal is in use, what is the polarity? Options are "
            "0-3 or 'none'.",
        )

        psr.add_argument(
            "--SetupProc",
            default=items["misc.use_setup_proc"],
            env_var="FESH_GEO_USE_SETUP_PROC",
            help="Drudg config: the answer for the drudg prompt for the use setup_proc for "
            "geodesy schedules, an option to write a `.snp` file that skips setup on scans "
            "when the mode hasn’t changed.",
        )

        psr.add_argument(
            "--VdifSingleThreadPerFile",
            default=items["misc.vdif_single_thread_per_file"],
            env_var="FESH_GEO_VDIF_SINGLE_THREAD_PER_FILE",
            help="VDIF single thread per file: only applies to Mark5C or Flexbuff recorders. Can "
            "be 'yes' or 'no'",
        )

        psr.add_argument(
            "--VCCServer",
            nargs="*",
            required=False,
            help="VCC server names (e.g. [NorthAmerica, Asia])",
        )
        psr.add_argument(
            "--VCCProtocol",
            nargs="*",
            required=False,
            help="Protocol to use for VCC servers (e.g. [http, http])",
        )
        psr.add_argument(
            "--VCCURL",
            nargs="*",
            required=False,
            help="VCC server URLSs (e.g. [76.123.156.0, 76.123.156.0])",
        )
        psr.add_argument(
            "--VCCPort",
            nargs="*",
            required=False,
            help="Port to use for VCC server (e.g. [8913, 8913])",
        )


        # psr.add_argument('-p', '--tpi-period', default=None, type=int, help="TPI period in centiseconds (0
        # = don't use the TPI Daemon, default). This can be set in the config file.")

        psr.add_argument(
            "-y",
            "--year",
            default=now.year,
            type=int,
            help="The year of the Master Schedule (default is this year)",
        )

        psr.add_argument(
            "-e",
            "--check",
            action="store_true",
            help="Check the current fesh3 status. Shows the status of schedule files and when schedule servers were "
            "last queried.",
        )

        psr.add_argument(
            "--monit",
            action="store_true",
            default=False,
            help="Similar to --check but text output format is intended for a FS monit interface",
        )

        psr.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="Runs fesh3 with all terminal output suppressed. Useful when running fesh3 as a service.",
        )

        return psr

    def station_label(self, station_name_2ch) -> str:
        """Used by Args class to check format of station ID strings

        Parameters
        ----------
        station_name_2ch station ID (punctuation etc will be removed)
        Returns
        -------
        Station name in 2-char IVS format

        """
        station_name_2ch = station_name_2ch.strip(string.punctuation).lower()
        if len(station_name_2ch) != 2:
            msg = 'Station name length wrong: "{}". Should be two characters.'.format(
                station_name_2ch
            )
            raise configargparse.ArgumentTypeError(msg)
        return station_name_2ch

    def _str2bool(self, val: Union[bool, str]) -> bool:
        """Takes an input value, either a boolean or a string, and returns a boolean.

        Parameters
        ----------
        val: input calue

        Returns
        -------
        bool: boolean value or raises an exception
        """
        if isinstance(val, bool):
            return val
        if val.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif val.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise configargparse.ArgumentTypeError("Boolean value expected.")


class CustomConfigParser(object):
    """Used by ConfigParser to read the skedf.ctl file"""

    def __init__(self, *args, **kwargs):
        super(CustomConfigParser, self).__init__(*args, **kwargs)

    def parse(self, stream: list) -> dict:
        """Parses a stream containing skedf.ctl lines and interprets them into a dictionary.

        Parameters
        ----------
        stream: a list of strings, one per line of skedf.ctl

        Returns
        -------
        items: dict of configuation parameters
        """
        items = OrderedDict()
        for i, line in enumerate(stream):
            line = line.strip()
            if not line or line[0] in ["*"]:
                # a comment or empty line
                continue
            space_and_comment_regex = r"(?P<space_comment>\!\s*.*)*"
            if line[0] in ["$"]:
                # A key match
                key_regex = r"\$(?P<key>.*)"
                key_match = re.match(key_regex + space_and_comment_regex + "$", line)
                if key_match:
                    key = key_match.group("key")
                    value = ""
                    items[key] = value.strip()
                    continue
            else:
                # its a value
                if key in ["catalogs", "schedules", "snap", "proc", "scratch"]:
                    # these have single values
                    value_regex = r"^\s*(?P<value>.+?)" + space_and_comment_regex + "$"
                    value_match = re.match(value_regex, line)
                    value = value_match.group("value")
                    items[key] = value.strip()
                    continue
                if key in ["print", "misc"]:
                    # these classify multiple key/value pairs
                    white_space = r"\s*"
                    key_val_regex = r"^\s*(?P<key>\w*)\s*(?P<value>.*?)"
                    match = re.match(
                        key_val_regex + space_and_comment_regex + "$", line
                    )
                    if match:
                        sub_key = match.group("key")
                        value = match.group("value")
                        newkey = "{}.{}".format(key, sub_key)
                        # if not items[newkey]:
                        #     items[newkey] = OrderedDict()
                        items[newkey] = value.strip()
                        continue
            raise "Unexpected line {} in {}: {}".format(
                i, getattr(stream, "name", "stream"), line
            )
        return items

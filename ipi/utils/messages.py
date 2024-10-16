"""Classes to print info, warnings and errors to standard output during the simulation."""

# This file is part of i-PI.
# i-PI Copyright (C) 2014-2015 i-PI developers
# See the "licenses" directory for full license information.


import traceback
import sys
import subprocess
import os
import socket
import platform
import multiprocessing

__all__ = [
    "Verbosity",
    "verbosity",
    "banner",
    "info",
    "warning",
    "get_identication_info",
]


VERB_QUIET = 0
VERB_LOW = 1
VERB_MEDIUM = 2
VERB_HIGH = 3
VERB_DEBUG = 4
VERB_TRACE = 5


class Verbosity(object):
    """Class used to determine what to print to standard output.

    Attributes:
        level: Determines what level of output to print.
    """

    lock = False
    level = VERB_LOW

    def __getattr__(self, name):
        """Determines whether a certain verbosity level is
        less than or greater than the stored value.

        Used to decide whether or not a certain info or warning string
        should be output.

        Args:
            name: The verbosity level at which the info/warning string
                will be output.
        """

        if name == "quiet":
            return self.level >= VERB_QUIET
        elif name == "low":
            return self.level >= VERB_LOW
        elif name == "medium":
            return self.level >= VERB_MEDIUM
        elif name == "high":
            return self.level >= VERB_HIGH
        elif name == "debug":
            return self.level >= VERB_DEBUG
        elif name == "trace":
            return self.level >= VERB_TRACE
        else:
            return super(Verbosity, self).__getattr__(name)

    def __setattr__(self, name, value):
        """Sets the verbosity level

        Args:
            name: The name of what to set. Should always be 'level'.
            value: The value to set the verbosity to.

        Raises:
            ValueError: Raised if either the name or the level is not
                a valid option.
        """

        if name == "level":
            if self.lock:
                # do not set the verbosity level if this is locked
                return
            if value == "quiet":
                level = VERB_QUIET
            elif value == "low":
                level = VERB_LOW
            elif value == "medium":
                level = VERB_MEDIUM
            elif value == "high":
                level = VERB_HIGH
            elif value == "debug":
                level = VERB_DEBUG
            elif value == "trace":
                level = VERB_TRACE
            else:
                raise ValueError(
                    "Invalid verbosity level " + str(value) + " specified."
                )
            super(Verbosity, self).__setattr__("level", level)
        else:
            super(Verbosity, self).__setattr__(name, value)


verbosity = Verbosity()


def get_git_info():
    try:
        # Get the current branch name
        branch_name = (
            subprocess.check_output(
                [
                    "git",
                    "-C",
                    os.path.dirname(__file__),
                    "rev-parse",
                    "--abbrev-ref",
                    "HEAD",
                ]
            )
            .strip()
            .decode("utf-8")
        )

        # Get the last commit hash
        last_commit = (
            subprocess.check_output(
                ["git", "-C", os.path.dirname(__file__), "log", "-1", "--format=%H"]
            )
            .strip()
            .decode("utf-8")
        )

        # Get the remote repository URL
        remote_url = (
            subprocess.check_output(
                [
                    "git",
                    "-C",
                    os.path.dirname(__file__),
                    "config",
                    "--get",
                    "remote.origin.url",
                ]
            )
            .strip()
            .decode("utf-8")
        )

        # Get commit author
        commit_author = (
            subprocess.check_output(
                ["git", "-C", os.path.dirname(__file__), "log", "-1", "--format=%an"]
            )
            .strip()
            .decode("utf-8")
        )

        # Get commit date
        # Get commit date in ISO 8601 format
        commit_date = (
            subprocess.check_output(
                [
                    "git",
                    "-C",
                    os.path.dirname(__file__),
                    "log",
                    "-1",
                    "--format=%cd",
                    "--date=format:%Y-%m-%d %H:%M:%S",
                ]
            )
            .strip()
            .decode("utf-8")
        )

        # Get commit message
        commit_message = (
            subprocess.check_output(
                ["git", "-C", os.path.dirname(__file__), "log", "-1", "--format=%s"]
            )
            .strip()
            .decode("utf-8")
        )

        return {
            "branch_name": branch_name,
            "last_commit": last_commit,
            "remote_url": remote_url,
            "commit_author": commit_author,
            "commit_date": commit_date,
            "commit_message": commit_message,
        }

    except subprocess.CalledProcessError:
        # Handle the case where the git command fails
        return None


def get_system_info():
    # Get the current working directory
    current_folder = os.getcwd()

    # Get the machine name (hostname)
    machine_name = ""
    try:
        machine_name = socket.gethostname()
    except Exception:
        pass

    # Get the system's fully qualified domain name (FQDN)
    fqdn = ""
    try:
        fqdn = socket.getfqdn()
    except Exception:
        pass

    # Get the operating system name
    os_name = ""
    try:
        os_name = platform.system()
    except Exception:
        pass

    # Get the operating system version
    os_version = ""
    try:
        os_version = platform.version()
    except Exception:
        pass

    # Get the processor name
    processor = ""
    try:
        processor = platform.processor()
    except Exception:
        pass

    # Get the number of CPUs or nodes available
    num_nodes = 0
    try:
        num_nodes = multiprocessing.cpu_count()
    except Exception:
        pass

    # Get the user name
    user_name = ""
    try:
        user_name = os.getlogin()
    except Exception:
        pass

    return {
        "current_folder": current_folder,
        "machine_name": machine_name,
        "fqdn": fqdn,
        "os_name": os_name,
        "os_version": os_version,
        "processor": processor,
        "num_nodes": num_nodes,
        "user_name": user_name,
    }


def get_identication_info():
    git_info = get_git_info()
    system_info = get_system_info()

    info_string = ""

    if git_info:
        info_string += "# Git information:\n"
        info_string += f"#      Remote URL: {git_info['remote_url']:<24}\n"
        info_string += f"#          Branch: {git_info['branch_name']:<24}\n"
        info_string += f"#     Last Commit: {git_info['last_commit']:<24}\n"
        info_string += f"#   Commit Author: {git_info['commit_author']:<24}\n"
        info_string += f"#  Commit Message: {git_info['commit_message']:<24}\n"
        info_string += f"#     Commit Date: {git_info['commit_date']:<24}\n"
    else:
        info_string += "# Unable to retrieve Git information.\n"

    info_string += "#\n"

    if system_info:
        info_string += "# System information:\n"
        info_string += f"#     Current Folder: {system_info['current_folder']}\n"
        info_string += f"#       Machine Name: {system_info['machine_name']}\n"
        info_string += f"#               FQDN: {system_info['fqdn']}\n"
        info_string += f"#   Operating System: {system_info['os_name']}\n"
        info_string += f"#         OS Version: {system_info['os_version']}\n"
        info_string += f"#          Processor: {system_info['processor']}\n"
        info_string += f"#     Number of CPUs: {system_info['num_nodes']}\n"
        info_string += f"#          User Name: {system_info['user_name']}\n"
    else:
        info_string += "# Unable to retrieve system information.\n"

    return info_string


def banner():
    """Prints out a banner."""

    print(
        r"""
 ____       ____       ____       ____
/    \     /    \     /    \     /    \
|  #################################  |
\__#_/     \____/     \____/     \_#__/
   #    _        _______  _____    #
   #   (_)      |_   __ \|_   _|   #      -*-     v 3.0.0-beta  -*-
   #   __  ______ | |__) | | |     #
   Y  [  ||______||  ___/  | |     #      A Universal Force Engine
  0 0  | |       _| |_    _| |_    #
   #  [___]     |_____|  |_____|   #
 __#_       ____       ____       _#__
/  # \     /    \     /    \     / #  \
|  #################################  |
\____/     \____/     \____/     \____/

    """
    )

    info_string = get_identication_info()
    print(info_string)


def info(text="", show=True):
    """Prints a message.

    Args:
        text: The text of the information message.
        show: A boolean describing whether or not the message should be
            printed.
    """

    if not show:
        return
    print(text)


def warning(text="", show=True):
    """Prints a warning message.

    Same as info, but with a "!W!" prefix and optionally printing a stack trace.

    Args:
        text: The text of the information message.
        show: A boolean describing whether or not the message should be
            printed.
    """

    if not show:
        return
    if verbosity.trace:
        traceback.print_stack(file=sys.stdout)
    print((" !W! " + text))

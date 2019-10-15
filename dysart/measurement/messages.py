"""
Standard output messages for displaying hierarchically-organized data such as
recursively-called status lines.
"""

import os
import logging
import getpass
import inspect
import datetime as dt
import textwrap
from functools import wraps

class Bcolor:
    """
    Enum class for colored printing
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'

def pprint_func(name, doc):
    """
    TODO real docstring for pprint_property
    Takes a name docstring of a function, an, and formats and pretty-prints them.
    """
    # Number of columns in the formatted docscring
    status_col = int(os.environ['STATUS_COL'])
    # Prepare the docstring: fix up whitespace for display
    doc = ' '.join(doc.strip().split())
    # Prepare the docstring: wrap it and indent it
    doc = '\t' + '\n\t'.join(textwrap.wrap(doc, status_col))
    # Finally, print the result
    print(cstr(name, status='bold') + '\n' + cstr(doc, status='italic') + '\n')
    

def cstr(s, status='normal'):
    """
    Wrap a string with ANSI color annotations
    """
    if status == 'ok':
        return Bcolor.OKGREEN + s + Bcolor.ENDC
    elif status == 'fail':
        return Bcolor.FAIL + s + Bcolor.ENDC
    elif status == 'warn':
        return Bcolor.WARNING + s + Bcolor.ENDC
    elif status == 'bold':
        return Bcolor.BOLD + s + Bcolor.ENDC
    elif status == 'italic':
        return Bcolor.ITALIC + s + Bcolor.ENDC
    elif status == 'underline':
        return Bcolor.UNDERLINE + s + Bcolor.ENDC
    else:
        return s

def cprint(s, status='normal', **kwargs):
    """
    Print a string with ANSI color annotations
    """
    print(cstr(s, status), **kwargs)

def msg1(message, level=0, end="\n"):
    """
    Print a formatted message to stdout.
    Accepts an optional level parameter, which is useful when you might wish
    to log a stack trace.
    """
    prompt = '=> '
    indent = '   '
    output = level * indent + prompt + message
    print(output, end=end)


def msg2(message, level=0, end="\n"):
    """
    Print a formatted message to stdout.
    Accepts an optional level parameter, which is useful when you might wish
    to log a stack trace.
    """
    prompt = '-> '
    indent = '   '
    output = level * indent + prompt + message
    print(output, end=end)


def write_log(message):
    """
    Write a message to a log file with date and time information.
    """
    logging.info(message)

def logged(stdout=True, message='log event', **kwargs):
    """
    Decorator for handling log messages. By default, writes to a default log
    file in the debug_data database directory, and prints output to stdout.
    Passes level parameter in decorated function to message functions to
    """
    # set terminator for log message
    term = "\n"
    if 'end' in kwargs:
        term = kwargs['end']

    def decorator(fn):
        @wraps(fn)
        def wrapped(*args_inner, **kwargs_inner):
            if stdout:
                if 'level' in kwargs_inner:
                    lvl = kwargs_inner['level']
                else:
                    lvl = 0
                msg1(message, level=lvl, end=term)

            # Check if this was called as a method of an object and, if so,
            # intercept the message to reflect this.
            # TODO: this could done much better with a log-entry object that
            # receives attributes like 'caller', etc., and is then formatted
            # independently.
            msg_prefix = ''
            spec = inspect.getargspec(fn)
            if spec.args and spec.args[0] == 'self':
                # TODO: note that this isn't really airtight. It is not a rule
                # of the syntax that argument 0 must be called 'self' for a 
                # class method.
                caller = args_inner[0]
                msg_prefix = caller.name + ' | '

            # write log message
            write_log(msg_prefix + message)
            # call the original function
            return_value = fn(*args_inner, **kwargs_inner)
            # post-call operations
            # ...
            # finally, return whatever fn would have returned!
            return return_value
        return wrapped
    return decorator

def configure_logging(logfile=''):
    """
    Set up the logging module to write to the correct logfile, etc.
    """

    if logfile is None or logfile is '':
        # Set the log output to the null file. This should actually be cross-
        # platform, i.e. equal to '/dev/null' on unix systems and 'NULL' on
        # windows.
        logfile = os.devnull

    # TODO: I should really take advantage of some of the more advanced
    # features of the logging module. 
    user = getpass.getuser()
    log_format = '%(asctime)s | ' + user + " | %(message)s"
    date_format = '%m/%d/%Y %I:%M:%S'
    logging.basicConfig(format=log_format, filename=logfile,
                        datefmt=date_format, level='INFO')
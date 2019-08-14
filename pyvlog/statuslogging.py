import sys
import json
import os
from datetime import datetime, timedelta
from copy import deepcopy


# Logging functions
def do_nothing(status):
    """
    Do absolutely nothing with each status

    Parameters
    ----------
    status : dict
        vlog status to be logged
    """
    pass


def print_status(status):
    """
    Print the timestamp of each logged status

    Parameters
    ----------
    status : dict
        vlog status to be logged
    """
    sys.stdout.write('\r{}'.format(status))


def append_status_to_list(status, status_list):
    """
    Append each logged status to a list object

    Parameters
    ----------
    status : dict
        vlog status to be logged
    status_list : list
        list to be appended to
    """
    status_list.append(deepcopy(status))


def append_status_to_file(status, filename):
    """
   Append each logged status to a file as a json

   Parameters
   ----------
   status : dict
       vlog status to be logged
   filename : str
       path to file to write to
   """

    # Convert datetime and timestamp data to isoformat and tenths of a second respectively
    status_out = {k:v for k,v in status.items()}
    for k,v in status_out.items():
        if type(v)==datetime:
            status_out[k] = v.isoformat()
        elif type(v)==timedelta:
            status_out[k] = v/timedelta(seconds=0.1)

    with open(filename, 'a') as f:
        json.dump(status_out, f)
        f.write(os.linesep)
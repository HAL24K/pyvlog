import sys
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

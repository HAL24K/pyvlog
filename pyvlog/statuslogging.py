import sys


# Logging functions
def print_status(status):
    """
    Print the timestamp of each logged status

    Parameters
    ----------
    status : dict
        vlog status to be logged
    """
    sys.stdout.write('\r{}'.format(status))
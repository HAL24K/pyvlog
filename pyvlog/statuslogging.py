import sys
import ujson


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

    # ujson seems the fastest way of copying a dict
    status_list.append(ujson.loads(ujson.dumps(status)))


def append_status_to_json(status, filename):
    """
   Append each logged status to a json file

   Parameters
   ----------
   status : dict
       vlog status to be logged
   filename : str
       path to file to write to
   """

    with open(filename, 'ab+') as f:
        f.seek(0, 2)
        if f.tell() == 0:
            # If empty then write full array
            f.write(ujson.dumps([status]).encode())
        else:
            # Otherwise append status to existing array
            f.seek(-1, 2)
            f.truncate()
            f.write(','.encode())
            f.write(ujson.dumps(status).encode())
            f.write(']'.encode())
from .pyvlog import VLogParser
from .statuslogging import *


def list_to_list(messages, logged_types=[]):
    """
    Convert a list of vlog messages to a list of statuses

    Parameters
    ----------
    messages : list
        list of vlog messages
    logged_types : list
        message types (should match keys of MESSAGE_TYPE_DICT) to be logged
        if empty all types are logged

    Returns
    ----------
    status_list : list
        list of statuses
    """

    status_list = []
    vlogger = VLogParser(append_status_to_list, logged_types=logged_types, status_list=status_list)

    for m in messages:
        vlogger.parse_message(m.strip())  # Remove any whitespace from the messages

    return status_list


def file_to_file(vlog_filename, out_filename, logged_types=[]):
    """
    Convert a file of vlog messages (each on a newline)
    to a file of json statuses (each on a new line)

    Parameters
    ----------
    vlog_filename : str
       path to file containing vlog messages
    out_filename : str
       path to file to write to
    logged_types : list
        message types (should match keys of MESSAGE_TYPE_DICT) to be logged
        if empty all types are logged

    Returns
    ----------
    status_list : list
        list of statuses
    """

    # Load the set of messages
    with open(vlog_filename, "rb") as f:
        messages = f.readlines()
    messages = [m.decode("utf-8").strip() for m in messages]

    vlogger = VLogParser(append_status_to_file, logged_types=logged_types, filename=out_filename)

    for m in messages:
        vlogger.parse_message(m.strip())  # Remove any whitespace from the messages

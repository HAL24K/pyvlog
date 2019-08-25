from .pyvlog import VLogParser
from .statuslogging import *
import pandas as pd
import collections


def flatten(d, parent_key='', sep='_'):
    """
    Flatten a nested dict

    Parameters
    ----------
    d : dict
        dictionary to flatten
    parent_key : str
        parent key to prefix new key
    sep : str
        separation character(s) for combined keys

    Returns
    ----------
    dict
        flattened dict
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + str(k) if parent_key else str(k)
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def list_to_list(messages, logged_types=['detectie', 'externeSignaalgroep']):
    """
    Convert a list of vlog messages to a list of statuses

    Parameters
    ----------
    messages : list
        list of vlog messages
    logged_types : list
        message types (should match keys of MESSAGE_TYPE_DICT) to be logged
        if empty list all types are logged

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


def list_to_file(messages, out_filename, logged_types=['detectie', 'externeSignaalgroep']):
    """
    Convert a list of vlog messages to a json file of statuses

    Parameters
    ----------
    messages : list
        list of vlog messages
    out_filename : str
       path to file to write to
    logged_types : list
        message types (should match keys of MESSAGE_TYPE_DICT) to be logged
        if empty list all types are logged
    """

    vlogger = VLogParser(append_status_to_json, logged_types=logged_types, filename=out_filename)

    for m in messages:
        vlogger.parse_message(m.strip())  # Remove any whitespace from the messages


def list_to_dataframe(messages, logged_types=['detectie', 'externeSignaalgroep']):
    """
    Convert a list of vlog messages to a list of statuses

    Parameters
    ----------
    messages : list
        list of vlog messages
    logged_types : list
        message types (should match keys of MESSAGE_TYPE_DICT) to be logged
        if empty list all types are logged

    Returns
    ----------
    df : pd.DataFrame
        dataframe of statuses
    """

    status_list = []
    vlogger = VLogParser(append_status_to_list, logged_types=logged_types, status_list=status_list)

    for m in messages:
        vlogger.parse_message(m.strip())  # Remove any whitespace from the messages

    # Flatten statuses
    status_list = [flatten(d) for d in status_list]
    df = pd.DataFrame(status_list)

    # Convert datetimes
    df["timestamp"] = pd.to_datetime(df["timestamp"]*1000000000)
    df["tijdReferentie"] = pd.to_datetime(df["tijdReferentie"] * 1000000000)
    df["deltaTijd"] = pd.to_timedelta(df["deltaTijd"]*1000000000)

    return df


def file_to_list(vlog_filename, logged_types=['detectie', 'externeSignaalgroep']):
    """
    Convert a file of vlog messages (each on a new line) to a list of statuses

    Parameters
    ----------
    vlog_filename : str
       path to file containing vlog messages
    logged_types : list
        message types (should match keys of MESSAGE_TYPE_DICT) to be logged
        if empty list all types are logged

    Returns
    ----------
    status_list : list
        list of statuses
    """

    # Load the set of messages
    with open(vlog_filename, "rb") as f:
        messages = f.readlines()
    messages = [m.decode("utf-8").strip() for m in messages]

    status_list = []
    vlogger = VLogParser(append_status_to_list, logged_types=logged_types, status_list=status_list)

    for m in messages:
        vlogger.parse_message(m.strip())  # Remove any whitespace from the messages

    return status_list


def file_to_file(vlog_filename, out_filename, logged_types=['detectie', 'externeSignaalgroep']):
    """
    Convert a file of vlog messages (each on a new line) to a json file of statuses

    Parameters
    ----------
    vlog_filename : str
       path to file containing vlog messages
    out_filename : str
       path to file to write to
    logged_types : list
        message types (should match keys of MESSAGE_TYPE_DICT) to be logged
        if empty list all types are logged
    """

    # Load the set of messages
    with open(vlog_filename, "rb") as f:
        messages = f.readlines()
    messages = [m.decode("utf-8").strip() for m in messages]

    vlogger = VLogParser(append_status_to_json, logged_types=logged_types, filename=out_filename)

    for m in messages:
        vlogger.parse_message(m.strip())  # Remove any whitespace from the messages


def file_to_dataframe(vlog_filename, logged_types=['detectie', 'externeSignaalgroep']):
    """
    Convert a file of vlog messages (each on a new line) to a list of statuses

    Parameters
    ----------
    vlog_filename : str
       path to file containing vlog messages
    logged_types : list
        message types (should match keys of MESSAGE_TYPE_DICT) to be logged
        if empty list all types are logged

    Returns
    ----------
    df : pd.DataFrame
        dataframe of statuses
    """

    # Load the set of messages
    with open(vlog_filename, "rb") as f:
        messages = f.readlines()
    messages = [m.decode("utf-8").strip() for m in messages]

    status_list = []
    vlogger = VLogParser(append_status_to_list, logged_types=logged_types, status_list=status_list)

    for m in messages:
        vlogger.parse_message(m.strip())  # Remove any whitespace from the messages

    # Flatten statuses
    status_list = [flatten(d) for d in status_list]
    df = pd.DataFrame(status_list)

    # Convert datetimes
    df["timestamp"] = pd.to_datetime(df["timestamp"] * 1000000000)
    df["tijdReferentie"] = pd.to_datetime(df["tijdReferentie"] * 1000000000)
    df["deltaTijd"] = pd.to_timedelta(df["deltaTijd"] * 1000000000)

    return df

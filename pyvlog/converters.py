"""
Functions for converting V-Log data into statuses.
"""


from .parsers import *
from .utils import flatten
import pandas as pd


def list_to_list(messages, logged_types=['detectie', 'externeSignaalgroep']):
    """
    Convert a list of v-log messages to a list of statuses.

    Parameters
    ----------
    messages : list
        List of v-log messages.
    logged_types : list
        Message types (should match keys of messagetypes.MESSAGE_TYPE_DICT) to be logged.
        If empty list all types are logged.

    Returns
    ----------
    status_list : list
        List of statuses.
    """

    status_list = []
    vlogger = VLogParserToList(status_list, logged_types=logged_types)

    for m in messages:
        vlogger.parse_message(m.strip())  # Remove any whitespace from the messages

    return status_list


def list_to_json(messages, path_to_json, logged_types=['detectie', 'externeSignaalgroep']):
    """
    Convert a list of v-log messages to a json file of statuses.

    Parameters
    ----------
    messages : list
        List of v-log messages.
    path_to_json : str
       Path to json file to write to.
    logged_types : list
        Message types (should match keys of messagetypes.MESSAGE_TYPE_DICT) to be logged.
        If empty list all types are logged.
    """

    vlogger = VLogParserToJson(path_to_json, logged_types=logged_types)

    for m in messages:
        vlogger.parse_message(m.strip())  # Remove any whitespace from the messages


def list_to_dataframe(messages, logged_types=['detectie', 'externeSignaalgroep']):
    """
    Convert a list of v-log messages to a dataframe of statuses.

    Parameters
    ----------
    messages : list
        List of vlog messages.
    logged_types : list
        Message types (should match keys of messagetypes.MESSAGE_TYPE_DICT) to be logged.
        If empty list all types are logged.

    Returns
    ----------
    df : pd.DataFrame
        Dataframe of statuses.
    """

    status_list = []
    vlogger = VLogParserToList(status_list, logged_types=logged_types)

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


def file_to_list(path_to_vlg, logged_types=['detectie', 'externeSignaalgroep']):
    """
    Convert a file of v-log messages (each on a new line) to a list of statuses.

    Parameters
    ----------
    path_to_vlg : str
       Path to file containing v-log messages.
    logged_types : list
        Message types (should match keys of messagetypes.MESSAGE_TYPE_DICT) to be logged.
        If empty list all types are logged.

    Returns
    ----------
    status_list : list
        List of statuses.
    """

    # Load the set of messages
    with open(path_to_vlg, "rb") as f:
        messages = f.readlines()
    messages = [m.decode("utf-8").strip() for m in messages]

    status_list = []
    vlogger = VLogParserToList(status_list, logged_types=logged_types)

    for m in messages:
        vlogger.parse_message(m.strip())  # Remove any whitespace from the messages

    return status_list


def file_to_json(path_to_vlg, path_to_json, logged_types=['detectie', 'externeSignaalgroep']):
    """
    Convert a file of v-log messages (each on a new line) to a json file of statuses.

    Parameters
    ----------
    path_to_vlg : str
       Path to file containing vlog messages.
    path_to_json : str
       Path to json file to write to.
    logged_types : list
        Message types (should match keys of messagetypes.MESSAGE_TYPE_DICT) to be logged.
        If empty list all types are logged.
    """

    # Load the set of messages
    with open(path_to_vlg, "rb") as f:
        messages = f.readlines()
    messages = [m.decode("utf-8").strip() for m in messages]

    vlogger = VLogParserToJson(path_to_json, logged_types=logged_types)

    for m in messages:
        vlogger.parse_message(m.strip())  # Remove any whitespace from the messages


def file_to_dataframe(path_to_vlg, logged_types=['detectie', 'externeSignaalgroep']):
    """
    Convert a file of v-log messages (each on a new line) to a dataframe of statuses.

    Parameters
    ----------
    path_to_vlg : str
       Path to file containing vlog messages.
    logged_types : list
        Message types (should match keys of messagetypes.MESSAGE_TYPE_DICT) to be logged.
        If empty list all types are logged.

    Returns
    ----------
    df : pd.DataFrame
        Dataframe of statuses.
    """

    # Load the set of messages
    with open(path_to_vlg, "rb") as f:
        messages = f.readlines()
    messages = [m.decode("utf-8").strip() for m in messages]

    status_list = []
    vlogger = VLogParserToList(status_list, logged_types=logged_types)

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

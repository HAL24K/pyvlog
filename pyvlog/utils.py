"""
Utility functions for converting hex messages and logging statuses.
"""


import collections


def hex_string_to_bits(string):
    """
    Convert a string of hex characters to bits.

    Parameters
    ----------
    string : str
        String of hex characters.

    Returns
    ----------
    bits : str
        Number of sensors in status.
    """

    bits = "".join(["{0:04b}".format(int(c, 16)) for c in string])

    return bits


def parse_internal_data(string):
    """
    Parse an element of internal phase data.

    Parameters
    ----------
    string : str
        Element of internal phase data.

    Returns
    ----------
    out_concise : dict
        Dictionary of internal phase status.
    """

    assert len(string) == 3, "Message wrong size"

    bits = hex_string_to_bits(string)

    out_concise = {
        'SR': bits[1],
        'MR': bits[2],
        'BR': bits[3],
        'AR': bits[4],
        'PR': bits[5],
        'A': bits[6],
        'CG': bits[7:]
    }

    for key, value in out_concise.items():
        out_concise[key] = int(value, 2)

    return out_concise


def parse_detection_data(string):
    """
    Parse an element of detection data.

    Parameters
    ----------
    string : str
        Element of detection data.

    Returns
    ----------
    out_concise : dict
        Dictionary of internal phase status.
    """
    assert len(string) == 1, "Message wrong size"

    bits = hex_string_to_bits(string)

    out_concise = {
        'OG-BG-FL': bits[:2],
        'storing': bits[2],
        'bezet': bits[3]
    }

    for key, value in out_concise.items():
        out_concise[key] = int(value, 2)

    return out_concise


def parse_instruction_data(string):
    """
    Parse an element of instruction variable status.

    Parameters
    ----------
    string : str
        Element of instruction data.

    Returns
    ----------
    out_concise : dict
        Dictionary of internal phase status.
    """

    assert len(string) == 2, "Message wrong size"

    bits = hex_string_to_bits(string)

    out_concise = {
        'TVG/MG': bits[3],
        'YV/VVAG': bits[4],
        'MK/H1H2': bits[5],
        'Z/AFK': bits[6],
        'FM/VMG': bits[7]
    }

    for key, value in out_concise.items():
        out_concise[key] = int(value, 2)

    return out_concise


def parse_ovhd_data(string):
    """
    Parse an element of ov/hulpdienst data.

    Parameters
    ----------
    string : str
        Element of internal phase data.

    Returns
    ----------
    out_concise : dict
        Dictionary of internal phase status.
    """

    assert len(string) == 4, "Message wrong size"

    bits = hex_string_to_bits(string)

    out_concise = {i: bits[-1 - i] for i in range(10)}

    for key, value in out_concise.items():
        out_concise[key] = int(value, 2)

    return out_concise


def flatten(d, parent_key='', sep='_'):
    """
    Flatten a nested dict.

    Parameters
    ----------
    d : dict
        Dictionary to flatten.
    parent_key : str
        Parent key to prefix new key.
    sep : str
        Separation character(s) for combined keys.

    Returns
    ----------
    dict
        Flattened dict.
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + str(k) if parent_key else str(k)
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

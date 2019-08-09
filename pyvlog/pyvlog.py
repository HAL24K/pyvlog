from datetime import datetime, timedelta

from .messagetypes import *


# Useful functions
def hex_string_to_bits(string):
    """
    Convert a string of hex characters to bits

    Parameters
    ----------
    string : str
        string of hex characters

    Returns
    ----------
    bits : str
        number of sensors in status
    """

    bits = "".join(["{0:04b}".format(int(c, 16)) for c in string])

    return bits


def parse_internal_data(string):
    """
    Parse an element of internal phase data

    Parameters
    ----------
    string : str
        element of internal phase data

    Returns
    ----------
    out_concise : dict
        dictionary of internal phase status
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
    Parse an element of detection data

    Parameters
    ----------
    string : str
        element of detection data

    Returns
    ----------
    out_concise : dict
        dictionary of internal phase status
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
    Parse an element of instruction variable status

    Parameters
    ----------
    string : str
        element of instruction data

    Returns
    ----------
    out_concise : dict
        dictionary of internal phase status
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
    Parse an element of ov/hulpdienst data

    Parameters
    ----------
    string : str
        element of internal phase data

    Returns
    ----------
    out_concise : dict
        dictionary of internal phase status
    """

    assert len(string) == 4, "Message wrong size"

    bits = hex_string_to_bits(string)

    out_concise = {i: bits[-1 - i] for i in range(10)}

    for key, value in out_concise.items():
        out_concise[key] = int(value, 2)

    return out_concise


# VLog parsing object
class VLogParser(object):
    """
    Object for parsing v-log messages

    Parameters
    ----------
    log_function : function
        function to be called each time the status is to be logged
        takes input self.status and **kwargs
    logged_types : list
        message types (should match keys of MESSAGE_TYPE_DICT) to be logged
    log_unconverted : bool
        if True the object will log all messages is is unable to convert
    """

    def __init__(self, log_function, logged_types=[], log_unconverted=False, **kwargs):

        if len(logged_types) == 0:
            logged_types = list(MESSAGE_TYPE_DICT.keys())

        assert set(logged_types).issubset(MESSAGE_TYPE_DICT.keys()), "logged types not understood"

        self.log_status = log_function
        self.log_kwargs = kwargs

        # Note which message types to log
        self.logged_types = [m_type for l_type in logged_types
                             for m_type in MESSAGE_TYPE_DICT[l_type]] + [1]  # Always log time

        # Set initial (empty) status
        self.status = {'timestamp': None,
                       'tijdReferentie': None}
        for key in logged_types:
            self.status[key] = {}

        self.log_unconverted = log_unconverted
        if self.log_unconverted:
            self.unconverted = []

    def _parse_status(self, message, data_size):
        """
        Parse the status part of a message

        Parameters
        ----------
        message : str
            vlog message
        data_size : float
            size of one data item, in hex

        Returns
        ----------
        num_sensors : int
            number of sensors in status
        """

        assert int(message[:2], 16) % 2 == 1, "Not status message"

        self.status['deltaTijd'] = timedelta(milliseconds=int(message[2:5], 16) * 100)
        self.update_time()
        num_sensors = int(hex_string_to_bits(message[5:8])[2:], 2)

        assert len(message[8:]) >= data_size * num_sensors, "Num sensors exceeds message length"

        return num_sensors

    def _parse_update(self, message, data_size):
        """
        Parse the update part of a message

        Parameters
        ----------
        message : str
            vlog message
        data_size : float
            size of one data item, in hex

        Returns
        ----------
        num_sensors : int
            number of sensors in status
        """

        assert int(message[:2], 16) % 2 == 0, "Not update message"

        self.status['deltaTijd'] = timedelta(milliseconds=int(message[2:5], 16) * 100)
        self.update_time()
        num_sensors = int(message[5], 16)

        assert len(message[6:]) >= data_size * num_sensors, "Num sensors exceeds message length"

        return num_sensors

    def parse_message(self, message):
        """
        Parse a v-log message and update the status

        Parameters
        ----------
        message : str
            vlog message
        """

        message_type = int(message[:2], 16)

        # Check if message is to be logged
        if message_type not in self.logged_types:
            if self.log_unconverted:
                self.unconverted.append(message)
            return

        if message_type == 1:
            # Time reference
            # Sometimes the time is given as 24:00 not 00:00 so add the time to the date to deal with this
            self.status['tijdReferentie'] = (
                    datetime(
                        int(message[2:6]),
                        int(message[6:8]),
                        int(message[8:10])
                    )
                    + timedelta(
                        hours=int(message[10:12]),
                        minutes=int(message[12:14]),
                        seconds=int(message[14:16]),
                        milliseconds=int(message[16]) * 100
                    )
            )
            self.status['deltaTijd'] = timedelta(0)

        elif message_type == 4:
            # V-Log information
            self.status['vlogInformatie']['V-Log versie'] = "{}.{}.{}".format(int(message[2:4], 16),
                                                                              int(message[4:6], 16),
                                                                              int(message[6:8], 16))
            vri_id = ''
            i = 8
            while i < len(message):
                vri_id += chr(int(message[i:i + 2], 16))
                i += 2
            self.status['vlogInformatie']['VRI id'] = vri_id.strip()  # Remove whitespace

        elif message_type == 5:
            # Detection status
            num_sensors = self._parse_status(message, data_size=1)
            for i in range(0, num_sensors):
                self.status['detectie'][i] = parse_detection_data(message[8 + i])

        elif message_type == 6:
            # Detection update
            num_sensors = self._parse_update(message, data_size=4)
            for i in range(0, num_sensors):
                index = int(message[6 + i * 4:8 + i * 4], 16)
                if index in self.status['detectie'].keys():
                    self.status['detectie'][index] = parse_detection_data(message[9 + i * 4])

        elif message_type == 7:
            # Other input status
            num_sensors = self._parse_status(message, data_size=0.25)
            status_bits = hex_string_to_bits(message[8:])
            for i in range(0, num_sensors):
                self.status['overigeIngangen'][i] = int(status_bits[i], 2)

        elif message_type == 8:
            # Other input update
            num_sensors = self._parse_update(message, data_size=2)
            for i in range(0, num_sensors):
                status_bits = hex_string_to_bits(message[6 + i * 2:8 + i * 2])
                index = int(status_bits[:-1], 2)
                if index in self.status['overigeIngangen'].keys():
                    self.status['overigeIngangen'][index] = int(status_bits[-1], 2)

        elif message_type == 9:
            # Internal phase status
            num_sensors = self._parse_status(message, data_size=3)
            for i in range(0, num_sensors):
                self.status['interneFaseCyclus'][i] = parse_internal_data(message[8 + i * 3:11 + i * 3])

        elif message_type == 10:
            # Internal phase update
            num_sensors = self._parse_update(message, data_size=6)
            for i in range(0, num_sensors):
                index = int(message[6 + i * 6:8 + i * 6], 16)
                if index in self.status['interneFaseCyclus'].keys():
                    self.status['interneFaseCyclus'][index] = parse_internal_data(message[9 + i * 6:12 + i * 6])

        elif message_type == 11:
            # Other output status (GUS)
            num_sensors = self._parse_status(message, data_size=0.25)
            status_bits = hex_string_to_bits(message[8:])
            for i in range(0, num_sensors):
                self.status['overigeUitgangenGUS'][i] = int(status_bits[i], 2)

        elif message_type == 12:
            # Other output update (GUS)
            num_sensors = self._parse_update(message, data_size=2)
            for i in range(0, num_sensors):
                status_bits = hex_string_to_bits(message[6 + i * 2:8 + i * 2])
                index = int(status_bits[:-1], 2)
                if index in self.status['overigeUitgangenGUS'].keys():
                    self.status['overigeUitgangenGUS'][index] = int(status_bits[-1], 2)

        elif message_type == 13:
            # External phase status
            num_sensors = self._parse_status(message, data_size=1)
            for i in range(0, num_sensors):
                self.status['externeSignaalgroep'][i] = int(message[8 + i], 16)

        elif message_type == 14:
            # External phase update
            num_sensors = self._parse_update(message, data_size=4)
            for i in range(0, num_sensors):
                index = int(message[6 + i * 4:8 + i * 4], 16)
                if index in self.status['externeSignaalgroep'].keys():
                    self.status['externeSignaalgroep'][index] = int(message[8 + i * 4:10 + i * 4], 16)

        elif message_type == 15:
            # Other output status (WUS)
            num_sensors = self._parse_status(message, data_size=0.25)
            status_bits = hex_string_to_bits(message[8:])
            for i in range(0, num_sensors):
                self.status['overigeUitgangenWUS'][i] = int(status_bits[i], 2)

        elif message_type == 16:
            # Other output update (WUS)
            num_sensors = self._parse_update(message, data_size=2)
            for i in range(0, num_sensors):
                status_bits = hex_string_to_bits(message[6 + i * 2:8 + i * 2])
                index = int(status_bits[:-1], 2)
                if index in self.status['overigeUitgangenWUS'].keys():
                    self.status['overigeUitgangenWUS'][index] = int(status_bits[-1], 2)

        elif message_type == 17:
            # Desired program status
            num_sensors = self._parse_status(message, data_size=1)
            for i in range(0, num_sensors):
                self.status['gewensteProgrammaStatus'][i] = int(message[8 + i], 16)

        elif message_type == 18:
            # Desired program update
            num_sensors = self._parse_update(message, data_size=2)
            for i in range(0, num_sensors):
                index = int(message[6 + i * 2], 16)
                if index in self.status['gewensteProgrammaStatus'].keys():
                    self.status['gewensteProgrammaStatus'][index] = int(message[7 + i * 2], 16)

        elif message_type == 19:
            # Actual program status
            num_sensors = self._parse_status(message, data_size=1)
            for i in range(0, num_sensors):
                self.status['werkelijkeProgrammaStatus'][i] = int(message[8 + i], 16)

        elif message_type == 20:
            # Actual program update
            num_sensors = self._parse_update(message, data_size=2)
            for i in range(0, num_sensors):
                index = int(message[6 + i * 2], 16)
                if index in self.status['werkelijkeProgrammaStatus'].keys():
                    self.status['werkelijkeProgrammaStatus'][index] = int(message[7 + i * 2], 16)

        elif message_type == 23:
            # Thermometer status
            num_sensors = self._parse_status(message, data_size=1)
            for i in range(0, num_sensors):
                status_bits = hex_string_to_bits(message[8 + i])
                self.status['thermometer'][i] = {'MVG': int(status_bits[-1], 2),
                                                 'RNA': int(status_bits[-2], 2)}

        elif message_type == 24:
            # Thermometer update
            num_sensors = self._parse_update(message, data_size=2)
            for i in range(0, num_sensors):
                status_bits = hex_string_to_bits(message[7 + i * 2])
                index = int(message[6 + i * 2], 16)
                if index in self.status['thermometer'].keys():
                    self.status['thermometer'][index] = {'MVG': int(status_bits[-1], 2),
                                                         'RNA': int(status_bits[-2], 2)}
        elif message_type == 32:
            # Instruction variable update
            num_sensors = self._parse_update(message, data_size=4)
            for i in range(0, num_sensors):
                index = int(message[6 + i * 4:8 + i * 4], 16)
                # Always add as no status for instruction variables
                self.status['instructieVariabelen'][index] = parse_instruction_data(message[8 + i * 4:10 + i * 4])

        elif message_type == 34:
            # OV/hulpdienst update
            num_sensors = self._parse_update(message, data_size=6)
            for i in range(0, num_sensors):
                index = int(message[6 + i * 6:8 + i * 6], 16)
                # Always add as no status for ov/hulpdienst update
                self.status['OVHulpdienstInformatie'][index] = parse_ovhd_data(message[8 + i * 6:12 + i * 6])

    def update_time(self):
        """
        Update the timestamp and if it has changed log the previous status

        Parameters
        ----------
        message : str
            vlog message
        """
        # Only log once we have seen a reference time
        if self.status['tijdReferentie'] and (self.status['timestamp']
                                              != (self.status['tijdReferentie'] + self.status['deltaTijd'])):

            # Log status and update time
            if self.status['timestamp']:
                self.log_status(self.status, **self.log_kwargs)
            self.status['timestamp'] = self.status['tijdReferentie'] + self.status['deltaTijd']

            # Wipe statuses which only exist at the timestamp of their production
            for key in WIPED_MESSAGES:
                if key in self.status.keys():
                    self.status[key] = {}
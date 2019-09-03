"""
Classes for parsing V-Log messages and logging statuses.
"""


from .messagetypes import *
from .utils import *
from datetime import datetime, timedelta
import ujson


class VLogParser(object):
    """
    Base class for parsing v-log messages.
    Does not log statuses.

    Parameters
    ----------
    logged_types : list
        Message types (should match keys of messagetypes.MESSAGE_TYPE_DICT) to be logged.
        If empty list all types are logged.
    """

    def __init__(self, logged_types=['detectie', 'externeSignaalgroep'], **kwargs):

        if len(logged_types) == 0:
            logged_types = list(MESSAGE_TYPE_DICT.keys())

        assert set(logged_types).issubset(MESSAGE_TYPE_DICT.keys()), "logged types not understood"

        self._log_kwargs = kwargs

        # Note which message types to log
        self.logged_types = [m_type for l_type in logged_types
                             for m_type in MESSAGE_TYPE_DICT[l_type]] + [1]  # Always log time

        # Set initial (empty) status
        self.status = {'timestamp': None,
                       'tijdReferentie': None}
        for key in logged_types:
            self.status[key] = {}

    def _parse_status(self, message, data_size):
        """
        Parse the status part of a message.

        Parameters
        ----------
        message : str
            V-log message.
        data_size : float
            Size of one data item, in hex.

        Returns
        ----------
        num_sensors : int
            Number of sensors in status.
        """

        assert int(message[:2], 16) % 2 == 1, "Not status message"

        self.status['deltaTijd'] = int(message[2:5], 16)/10 # Log in seconds
        self._update_time()
        num_sensors = int(hex_string_to_bits(message[5:8])[2:], 2)

        assert len(message[8:]) >= data_size * num_sensors, "Num sensors exceeds message length"

        return num_sensors

    def _parse_update(self, message, data_size):
        """
        Parse the update part of a message.

        Parameters
        ----------
        message : str
            V-log message.
        data_size : float
            Size of one data item, in hex.

        Returns
        ----------
        num_sensors : int
            Number of sensors in status.
        """

        assert int(message[:2], 16) % 2 == 0, "Not update message"

        self.status['deltaTijd'] = int(message[2:5], 16)/10 # Log in seconds
        self._update_time()
        num_sensors = int(message[5], 16)

        assert len(message[6:]) >= data_size * num_sensors, "Num sensors exceeds message length"

        return num_sensors

    def parse_message(self, message):
        """
        Parse a v-log message and update the status.
        If the status is complete log_status is called.

        Parameters
        ----------
        message : str
            V-log message.
        """

        message_type = int(message[:2], 16)

        # Check if message is to be logged
        if message_type not in self.logged_types:
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
            ).timestamp()
            self.status['deltaTijd'] = 0

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

    def _update_time(self):
        """
        Update the timestamp and if it has changed log the previous status.
        """
        # Only log once we have seen a reference time
        if self.status['tijdReferentie'] and (self.status['timestamp']
                                              != (self.status['tijdReferentie'] + self.status['deltaTijd'])):

            # Log status and update time
            if self.status['timestamp']:
                self.log_status(self.status, **self._log_kwargs)
            self.status['timestamp'] = self.status['tijdReferentie'] + self.status['deltaTijd']

            # Wipe statuses which only exist at the timestamp of their production
            for key in WIPED_MESSAGES:
                if key in self.status.keys():
                    self.status[key] = {}

    def log_status(self, status):
        """
        Placeholder function, does nothing with the status.

        Parameters
        ----------
        status : dict
            V-log status to be logged.
        """

        pass


class VLogParserToList(VLogParser):
    """
    Class for parsing v-log messages to a list of statuses.
    Appends each logged status to a list object.

    Parameters
    ----------
    status_list : list
        List to be appended to.
    logged_types : list
        Message types (should match keys of messagetypes.MESSAGE_TYPE_DICT) to be logged.
        If empty list all types are logged.
    """

    def __init__(self, status_list, logged_types=['detectie', 'externeSignaalgroep']):

        super().__init__(logged_types, status_list=status_list)

    def log_status(self, status, status_list):
        """
        Append the status to a list.

        Parameters
        ----------
        status : dict
            V-log status to be logged.
        status_list : list
            List to be appended to.
        """

        # ujson seems the fastest way of copying a dict
        status_list.append(ujson.loads(ujson.dumps(status)))


class VLogParserToJson(VLogParser):
    """
    Class for parsing v-log messages to a json of statuses.
    Appends each logged status to a json file.

    Parameters
    ----------
    path_to_json : str
       Path to json file.
    logged_types : list
        Message types (should match keys of messagetypes.MESSAGE_TYPE_DICT) to be logged.
        If empty list all types are logged.
    """

    def __init__(self, path_to_json, logged_types=['detectie', 'externeSignaalgroep']):

        super().__init__(logged_types, path_to_json=path_to_json)

    def log_status(self, status, path_to_json):
        """
        Append the status to a json file.

        Parameters
        ----------
        status : dict
            V-log status to be logged.
        path_to_json : str
            Path to json file.
        """

        with open(path_to_json, 'ab+') as f:
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
# pyvlog

## Overview

**pyvlog** is a Python package for working with traffic device data from smart intersections that adhere to the [V-Log messaging protocol](http://www.v-log.nl/). It can be used to convert sequences of device messages into time-stamped statuses for any combination of traffic devices at a smart intersection.

It converts individual device messages like this:
```
012018091115000000
05000003000
0D00000200
090000020070A0
0E00310102
0600610201
```
into intersection statuses like this:
```
{'timestamp': 1536670800.6,
 'tijdReferentie': 1536670800.0,
 'detectie': {0: {'OG-BG-FL': 0, 'storing': 0, 'bezet': 0},
  1: {'OG-BG-FL': 0, 'storing': 0, 'bezet': 0},
  2: {'OG-BG-FL': 0, 'storing': 0, 'bezet': 1}},
 'externeSignaalgroep': {0: 0, 1: 2},
 'deltaTijd': 0.6}
```

Naming and data conventions for the various traffic devices follow the specification provided by [Vialis](https://www.ivera.nl/wp-content/uploads/2018/04/V-Log_protocol_en_definities_v3.01_WG_techniek_changes_highlighted.pdf).

## Installation

pyvlog can be installed via pip:

```
pip install pyvlog
```

## Documentation

Documentation is available at [readthedocs](https://pyvlog.readthedocs.io/).

## How to use pyvlog

pyvlog is designed for converting sequences of v-log messages - streamed from smart intersection traffic devices - into time-stamped statuses of all traffic devices at an intersection. These statuses can be queried by both time and device, aiding the development of functionality built around v-log data.

pyvlog is able to perform this conversion in two ways.

_parsers_ are objects which receive messages individually and use each message to update the stored intersection status. Additionally they can identify when a status is "complete" (all values are known for a specific timestamp) and can log these completed statuses. They are suited to converting realtime streams of v-log messages.

_converters_ are functions which take a sequence of v-log messages and return a sequence of statuses. They are suited to (batch) converting data dumps of historic v-log messages.

### Parse sequences of v-log data

The parsing of individual v-log messages is always done by the `VLogParser` class. At its simplest, you can create a `VLogParser()` object and call its `.parse_message()` method one message at a time on a sequence of messages. The object stores the intersection status as a dictionary in the attribute `.status`. This is the intersection status after the last message was received.

```python
from pyvlog.parsers import VLogParser

vlogger = VLogParser()

messages = ['012018091115000000', '05000003000', '0D00000200', '090000020070A0', '0E00310102', '0600610201']
for m in messages:
    vlogger.parse_message(m)
    
print(vlogger.status)
```

When converting a sequence of v-log messages you may well want to know the status of the intersection for all timestamps spanned by the sequence of messages, not just the final status. The `VLogParser` class identifies when a status is complete (there is not a one-to-one correspondence between messages and statuses) and logs this status by calling the method `.log_status()`.

The base `VLogParser` class does not store these logged statuses anywhere, however two child classes are provided, `VLogParserToList` and `VLogParserToJson`, which log the statuses to a list and a JSON file respectively.

```python
from pyvlog.parsers import VLogParserToList

status_list = []
vlogger = VLogParserToList(status_list)

messages = ['012018091115000000', '05000003000', '0D00000200', '090000020070A0', '0E00310102', '0600610201']
for m in messages:
    vlogger.parse_message(m)
    
print(status_list)
```

Instructions on writing your own parser classes are provided below.

### Convert v-log files to historic statuses

A number of converter functions are provided for converting complete sets of v-log messages into their corresponding time-stamped statuses. These convert from a file or list of v-log messages to a JSON file, list or pandas dataframe of historic statuses (e.g. `file_to_file` or `list_to_dataframe`). Status data is written in JSON format, using UltraJSON.

```python
from pyvlog.converters import file_to_json

vlog_file = "test.vlg"
out_file = "test.json"
file_to_json(vlog_file, out_file)
```

For conversion to pandas dataframes the status dictionary is flattened (with "\_" joining the keys) and timing fields are converted to datetime / timedelta.

```python
from pyvlog.converters import list_to_dataframe

messages = ['012018091115000000', '05000003000', '0D00000200', '090000020070A0', '0E00310102', '0600610201']
df = list_to_dataframe(messages)

print(df.head())
```

### Write custom v-log parsers for your projects

Custom parser classes can be created for any number of different logging routines, simply by inheriting the base `VLogParser` class and defining a new `.log_status()` method, plus any additional arguments. The two additional classes defined in the `parsers` module, `VLogParserToList` and `VLogParserToJson`, illustrate how such a custom parsing class may be created.

### Traffic device coverage

This package is developed for the processing of realtime v-log messages from a small number of smart intersections. As such not all types of v-log messages were available during its development. The message types currently parsed are given by the keys of `messagetypes.MESSAGE_TYPE_DICT` and are repeated below (with the v-log message prefix given in brackets).

#### Message types parsed:
- _tijdReferentie_ (1)
- _vlogInformatie_ (4)
- _detectie_ (5,6)
- _overigeIngangen_ (7,8)
- _interneFaseCyclus_ (9,10)
- _overigeUitgangenGUS_ (11,12)
- _externeSignaalgroep_ (13,14)
- _overigeUitgangenWUS_ (15,16)
- _gewensteProgrammaStatus_ (17,18)
- _werkelijkeProgrammaStatus_ (19,20)
- _thermometer_ (23,24)
- _instructieVariabelen_ (32)
- _OVHulpdienstInformatie_ (34)

By default only _detectie_ and _externeSignaalgroep_ are parsed (plus _tijdReferentie_, which is always parsed in order to calculate the timestamp). Both the parser classes and converter functions take an argument `logged_types`, which specifies which message types to log.

```python
from pyvlog.parsers import VLogParser

vlogger = VLogParser(logged_types=["detectie", "externeSignaalgroep", "interneFaseCyclus"])

messages = ['012018091115000000', '05000003000', '0D00000200', '090000020070A0', '0E00310102', '0600610201']
for m in messages:
    vlogger.parse_message(m)
    
print(vlogger.status)
```

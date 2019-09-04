# pyvlog

## Overview

**pyvlog** is a Python package for working with traffic device data from smart intersections that adhere to the [V-Log messaging protocol](http://www.v-log.nl/). It can be used to convert sequences of device messages into time-stamped statuses for any combination of traffic devices at a smart intersection.

It converts individual device messages like this:
```
012018091115000000
05000003000
0D00000200
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

pyvlog can be installed from this repository via pip:

```
pip install git+https://github.com/hal24k/pyvlog.git
```

## Documentation

Documentation is available at [readthedocs](https://pyvlog.readthedocs.io/).

## How to use pyvlog

pyvlog is designed for converting sequences of v-log messages - streamed from smart intersection traffic devices - into time-stamped statuses for all traffic devices at an intersection. These statuses can be queried by both time and device, aiding the development of functionality built around v-log data.

pyvlog is able to perform this conversion in two ways.

_parsers_ are objects which receive messages individually and use each message to update the stored intersection status. Additionally they can identify when a status is "complete" (all values are known for a specific timestamp) and can log these completed statuses. They are suited to converting realtime streams of v-log messages.

_converters_ are functions which take a sequence of v-log messages and return a sequence of statuses. They are suited to (batch) converting data dumps of historic v-log messages.

### Parse sequences of v-log data

The parsing of individual v-log messages is always done by the `VLogParser` class. At its simplest, you can create a `VLogParser()` object and call its `.parse_message()` method one message at a time on a sequence of messages. The object stores the intersection status in the attribute `.status`. This is the intersection status after the last message was received.

```python
messages = ['012018091115000000', '05000003000', '0D00000200', '0E00310102', '0600610201']

from pyvlog.parsers import VLogParser
vlogger = VLogParser()

for m in messages:
    vlogger.parse_message(m)
    
print(vlogger.status)
```

When converting a sequence of v-log messages you may well want to know the status of the intersection for all timestamps spanned by the sequence of messages, not just the final status. The `VLogParser` class identifies when a status is complete (there is not a one-to-one correspondence between messages and statuses) and logs this status by calling the method `.log_status()`.

The base `VLogParser` class does not store these logged statuses anywhere, however two child classes are provided, `VLogParserToList` and `VLogParserToJson`, which log the statuses to a list and a JSON file respectively.

```python
messages = ['012018091115000000', '05000003000', '0D00000200', '0E00310102', '0600610201']
status_list = []

from pyvlog.parsers import VLogParserToList
vlogger = VLogParserToList(status_list)

for m in messages:
    vlogger.parse_message(m)
    
print(status_list)
```

Instructions on writing your own `VLogParserTo*` classes are provided below.

### Convert v-log files to json

### Write custom v-log parsers for your projects

### Traffic device coverage

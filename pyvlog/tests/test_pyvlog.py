from pyvlog.pyvlog import VLogParser
from pyvlog.statuslogging import do_nothing

def test_parsing():

    # Load the test set of messages
    with open("pyvlog/data/test.vlg", "rb") as f:
        messages = f.readlines()
    messages = [m.decode("utf-8").strip() for m in messages]

    # Run them through the vlog parser
    vlogger = VLogParser(do_nothing)
    for m in messages:
        vlogger.parse_message(m)
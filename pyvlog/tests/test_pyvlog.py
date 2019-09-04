from pyvlog.parsers import VLogParser
import ujson


def id_dict(obj):
    return obj.__class__.__name__ == 'dict'


def contains_key_rec(v_key, v_dict):
    for curKey in v_dict:
        if curKey == v_key or (id_dict(v_dict[curKey]) and contains_key_rec(v_key, v_dict[curKey])):
            return True
    return False


def get_value_rec(v_key, v_dict):
    for curKey in v_dict:
        if curKey == v_key:
            return v_dict[curKey]
        elif id_dict(v_dict[curKey]) and get_value_rec(v_key, v_dict[curKey]):
            return contains_key_rec(v_key, v_dict[curKey])
    return None


def test_parsing():

    # Load the test set of messages
    with open("pyvlog/data/test.vlg", "rb") as f:
        messages = f.readlines()
    messages = [m.decode("utf-8").strip() for m in messages]

    # Run them through the vlog parser
    vlogger = VLogParser(logged_types=[])
    for m in messages:
        vlogger.parse_message(m)

    # Load the expected output
    with open("pyvlog/data/test.json", "rb") as f:
        last_status = ujson.load(f)[0]

    # Check both dictionaries are the same by comparing json strings
    assert ujson.dumps(last_status) == ujson.dumps(vlogger.status), "Converted status does not agree with reference"

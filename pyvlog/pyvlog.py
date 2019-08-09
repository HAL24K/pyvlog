def hex_string_to_bits(string):
    """Convert a string of hex characters to bits"""
    return "".join(["{0:04b}".format(int(c, 16)) for c in string])

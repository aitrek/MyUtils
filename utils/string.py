"""Utilities for string"""


def sbc_to_dbc(sbc):
    """Convert SBC case to DBC case"""
    def convert(c):
        ucode = ord(c)
        if ucode == 12288:
            return chr(32)
        elif 65281 <= ucode <= 65374:
            return chr(ucode - 65248)
        else:
            return c
    return "".join([convert(c) for c in sbc])

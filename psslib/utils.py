#-------------------------------------------------------------------------------
# pss: utils.py
#
# Some miscellaneous utilities for pss.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from .py3compat import int2byte, str2bytes
from . import colorama


_text_characters = (
        b''.join(int2byte(i) for i in range(32, 127)) +
        b'\n\r\t\f\b')

def istextfile(fileobj, blocksize=512):
    """ Uses heuristics to guess whether the given file is text or binary,
        by reading a single block of bytes from the file.
        If more than 30% of the chars in the block are non-text, or there
        are NUL ('\x00') bytes in the block, assume this is a binary file.
    """
    block = fileobj.read(blocksize)

    # With -U the file will be open in text mode,
    # so a read (in python 3) won't return bytes.
    if not isinstance(block, bytes):
        block = str2bytes(block)

    if b'\x00' in block:
        # Files with null bytes are binary
        return False
    elif not block:
        # An empty file is considered a valid text file
        return True

    # Use translate's 'deletechars' argument to efficiently remove all
    # occurrences of _text_characters from the block
    nontext = block.translate(None, _text_characters)
    return float(len(nontext)) / len(block) <= 0.30


def decode_colorama_color(color_str):
    """ Decode a Colorama color encoded in a string in the following format:
        FORE,BACK,STYLE

        FORE: foreground color (one of colorama.Fore)
        BACK: background color (one of colorama.Back)
        STYLE: style (one of colorama.Style)

        For example, for CYAN text on GREEN background with a DIM style
        (pretty, aye?) the input should be: CYAN,GREEN,DIM

        BACK and STYLE are optional. If STYLE is not specified, the default is
        colorama.Style.NORMAL. If BACK is not specified, the default is
        colorama.Back.BLACK.

        Return the colorama color, or None if there's a problem decoding.
    """
    if not color_str:
        return None

    # Split the input and add defaults. After this, parts is a 3-element list
    parts = color_str.split(',')
    if len(parts) == 1:
        parts.append('RESET')
    if len(parts) == 2:
        parts.append('NORMAL')

    try:
        c_fore = getattr(colorama.Fore, parts[0])
        c_back = getattr(colorama.Back, parts[1])
        c_style = getattr(colorama.Style, parts[2])
        return c_fore + c_back + c_style
    except AttributeError:
        return None




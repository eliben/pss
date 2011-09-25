#-------------------------------------------------------------------------------
# pss: utils.py
#
# Some utilities
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------


_text_characters = "".join(map(chr, range(32, 127))) + "\n\r\t\b"


def istextfile(fileobj, blocksize=512):
    """ Uses heuristics to guess whether the given file is text or binary, by
        reading a single block of text from the file.
        Somewhat similar to Perl's -T operator, but simplified (doesn't take 
        unicode into consideration)
        The main heuristic is: if more than 30% of the chars in the block are
        non-text, assume this is a binary file.
    """
    block = fileobj.read(blocksize)
    if '\0' in block:
        # Files with null bytes are binary
        return False
    elif not block:
        # An empty file is considered a valid text file
        return True

    # Use translate's 'deletechars' argument to efficiently remove all
    # occurrences of text_characters from the block
    nontext = block.translate(None, _text_characters)

    return float(len(nontext)) / len(block) <= 0.30


import os, sys, tempfile
import unittest

sys.path.insert(0, '.')
sys.path.insert(0, '..')
from psslib.defaultpssoutputformatter import DefaultPssOutputFormatter


class TestOutputFormatter(unittest.TestCase):
    def setUp(self):
        self.filename = 'test_outputformatter.txt'
        self.stream = open(self.filename, 'w')
        self.formatter = DefaultPssOutputFormatter(do_colors=False, stream=self.stream)

    def tearDown(self):
        os.remove(self.filename)

    def _get_contents(self):
        self.stream.close()
        with open(self.filename, 'rb') as f:
            return f.read()

    def test_eol(self):
        self.formatter.context_line('LINE\r\n', 42, 'FILENAME')
        contents = self._get_contents()
        self.assertTrue('\r\r\n' not in contents)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

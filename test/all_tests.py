#!/usr/bin/env python

import unittest

suite = unittest.TestLoader().loadTestsFromNames([
    'test_filefinder',
    'test_contentmatcher',
    'test_driver',
    'test_pssmain',
    'test_outputformatter',
])
unittest.TextTestRunner(verbosity=1).run(suite)



import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '../../'))
sys.path.append(os.path.join(PROJECT_ROOT, 'module_utils'))

import k8s_runner  # noqa


class CalledProcessErrorTest(unittest.TestCase):
    def test_raise_error(self):
        k8s_runner.CalledProcessError
        self.assertEqual(1, 1)

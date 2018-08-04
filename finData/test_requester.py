# This Python file uses the following encoding: utf-8
from finData.requester import Requester
from finData.testing_utils import *


class RequesterSetup(unittest.TestCase):

    def setUp(self):
        stock = MagicMock()
        self.req = Requester(stock)

    def test_unknowntable(self):
        hist = MagicMock()
        tab = MagicMock()
        tab.name = 'unknown_table'
        with self.assertRaises(AttributeError):
            self.req.table(tab, hist)

# This Python file uses the following encoding: utf-8
from finData.requester import Requester
from finData.testing_utils import *


class RequesterSetup(unittest.TestCase):

    def setUp(self):
        stock = MagicMock()
        self.req = Requester(stock)
        self.hist = MagicMock()
        self.tab = MagicMock()

    def test_unknowntable(self):
        self.tab.name = 'unknown_table'
        with self.assertRaises(AttributeError):
            self.req.table(self.tab, self.hist)

    def test_fund(self):
        self.tab.name = 'fundamental_yearly'
        with patch('finData.requester.Requester._getFundData') as scraper:
            scraper.return_value = 'fund'
            res = self.req.table(self.tab, self.hist)
        self.assertEqual(res, 'fund')

    def test_divid(self):
        self.tab.name = 'divid_yearly'
        with patch('finData.requester.Requester._getDividData') as scraper:
            scraper.return_value = 'divid'
            res = self.req.table(self.tab, self.hist)
        self.assertEqual(res, 'divid')

    def test_hist(self):
        self.tab.name = 'hist_daily'
        res = self.req.table(self.tab, self.hist)
        self.assertEqual(res, 'hist')

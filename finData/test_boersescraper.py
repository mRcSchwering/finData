# This Python file uses the following encoding: utf-8
from finData.boersescraper import BoerseScraper
from finData.testing_utils import *

ads = ['Adidas-Aktie', 'DE000A1EWWW0']
bion = ['BB-Biotech-Aktie', 'CH0038389992']
dummy = ['abc.de', 'XXXXX']

with open('finData/testdata/divid.html') as inf:
    DIVID_DATA = inf.read()
with open('finData/testdata/fund.html') as inf:
    FUND_DATA = inf.read()


class BoerseScraperSetup(unittest.TestCase):

    def setUp(self):
        self.a = BoerseScraper(*ads)
        self.b = BoerseScraper(*bion)

    def test_URLsCorreceltyResolved(self):
        self.b._resolve_boerse_url('dividenden')
        exp = 'https://www.boerse.de/dividenden/BB-Biotech-Aktie/CH0038389992'
        self.assertEqual(self.b._url, exp)
        self.a._resolve_boerse_url('fundamental-analyse')
        exp = 'https://www.boerse.de/fundamental-analyse/Adidas-Aktie/DE000A1EWWW0'
        self.assertEqual(self.a._url, exp)


class ScrapeHTMLTables(unittest.TestCase):

    def setUp(self):
        self.s = BoerseScraper(*dummy)
        self.s._requestURL = MagicMock(return_value=bytes(DIVID_DATA, 'utf-8'))

    def test_dividendenFound(self):
        self.s._requestURL = MagicMock(return_value=bytes(DIVID_DATA, 'utf-8'))
        tab = self.s._getHTMLTable('Dividenden', 'url')
        self.assertEqual(len(tab), 46)
        self.assertEqual(type(tab).__name__, 'Tag')

    def test_dividendenFound(self):
        self.s._requestURL = MagicMock(return_value=bytes(DIVID_DATA, 'utf-8'))
        tab = self.s._getHTMLTable('Dividenden', 'url')
        self.assertEqual(len(tab), 46)
        self.assertEqual(type(tab).__name__, 'Tag')

    def test_searchTextNotFound(self):
        self.s._requestURL = MagicMock(return_value=bytes(DIVID_DATA, 'utf-8'))
        with self.assertRaises(AttributeError):
            self.s._getHTMLTable('asd', 'url')

#
# class HTMLtab2dict(unittest.TestCase):
#
#     def setUp(self):
#         self.s = BoerseScraper(*dummy)
#         with open('finData/testdata/divid.html') as inf:
#             testdata = inf.read()
#         self.s._requestURL = MagicMock(return_value=bytes(testdata, 'utf-8'))
#
#     def test_searchTextFound(self):
#         tab = self.s._getHTMLTable('Dividenden', 'url')
#         self.assertEqual(len(tab), 46)
#         self.assertEqual(type(tab).__name__, 'Tag')
#
#     def test_searchTextNotFound(self):
#         with self.assertRaises(AttributeError):
#             self.s._getHTMLTable('asd', 'url')

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

    def test_dividendenFound(self):
        self.s._requestURL = MagicMock(return_value=bytes(DIVID_DATA, 'utf-8'))
        tabs = self.s._getHTMLTables(['Dividenden'], 'url')
        self.assertEqual(len(tabs), 1)
        self.assertEqual(len(tabs['Dividenden']), 46)
        self.assertEqual(type(tabs['Dividenden']).__name__, 'Tag')

    def test_allFundsFound(self):
        self.s._requestURL = MagicMock(return_value=bytes(FUND_DATA, 'utf-8'))
        search_texts = ['GuV', 'Bilanz', 'Kennzahlen', 'Rentabilität',
                        'Personal', 'Marktkapitalisierung']
        lens = [17, 25, 20, 11, 12, 6]
        tabs = self.s._getHTMLTables(search_texts, 'url')
        self.assertEqual(len(tabs), 6)
        for i in range(len(lens)):
            self.assertEqual(len(tabs[search_texts[i]]), lens[i])
            self.assertEqual(type(tabs[search_texts[i]]).__name__, 'Tag')

    def test_searchTextNotFound(self):
        self.s._requestURL = MagicMock(return_value=bytes(DIVID_DATA, 'utf-8'))
        with self.assertRaises(AttributeError):
            self.s._getHTMLTables(['asd'], 'url')


class GuVHTMLtable2dict(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.s = BoerseScraper(*dummy)
        cls.s._requestURL = MagicMock(return_value=bytes(FUND_DATA, 'utf-8'))
        cls.tabs = cls.s._getHTMLTables(['GuV'], 'url')

    def test_defaultConversion(self):
        d = self.s._htmlTab2dict(self.tabs['GuV'])
        self.assertEqual(set(d.keys()), set(['colnames', 'rownames', 'data']))
        exp = [b'2009', b'2010', b'2011', b'2012', b'2013', b'2014', b'2015', b'2016', b'2017']
        self.assertEqual(d['colnames'], exp)
        exp = [b'Umsatz', b'Bruttoergebnis', b'Operatives Ergebnis (EBIT)', b'Ergebnis vor Steuer (EBT)', b'Jahres\xc3\xbcberschuss', b'Dividendenaussch\xc3\xbcttung']
        self.assertEqual(d['rownames'], exp)
        self.assertEqual(len(d['data']), 6)
        self.assertEqual(len(d['data'][0]), 9)

    def test_rownamesFalse(self):
        with self.assertRaises(AttributeError):
            self.s._htmlTab2dict(self.tabs['GuV'], hasRownames=False)
        d = self.s._htmlTab2dict(self.tabs['GuV'], hasRownames=False, validateTable=False)
        self.assertEqual(set(d.keys()), set(['colnames', 'data']))
        exp = [b'', b'2009', b'2010', b'2011', b'2012', b'2013', b'2014', b'2015', b'2016', b'2017']
        self.assertEqual(d['colnames'], exp)
        self.assertEqual(len(d['data']), 7)
        self.assertEqual(len(d['data'][0]), 10)
        self.assertEqual(len(d['data'][1]), 10)
        self.assertEqual(len(d['data'][6]), 1)

    def test_colnamesFalse(self):
        d = self.s._htmlTab2dict(self.tabs['GuV'], hasColnames=False)
        self.assertEqual(set(d.keys()), set(['rownames', 'data']))
        exp = [b'', b'Umsatz', b'Bruttoergebnis', b'Operatives Ergebnis (EBIT)', b'Ergebnis vor Steuer (EBT)', b'Jahres\xc3\xbcberschuss', b'Dividendenaussch\xc3\xbcttung']
        self.assertEqual(exp, d['rownames'])
        self.assertEqual(len(d['data']), 7)
        self.assertEqual(len(d['data'][0]), 9)
        self.assertEqual(len(d['data'][1]), 9)
        self.assertEqual(len(d['data'][6]), 9)

    def test_rowAndColNamesFalse(self):
        with self.assertRaises(AttributeError):
            self.s._htmlTab2dict(self.tabs['GuV'], hasColnames=False, hasRownames=False)
        d = self.s._htmlTab2dict(self.tabs['GuV'], hasColnames=False, hasRownames=False, validateTable=False)
        self.assertEqual(set(d.keys()), set(['data']))
        self.assertEqual(len(d['data']), 8)
        self.assertEqual(len(d['data'][0]), 10)
        self.assertEqual(len(d['data'][1]), 10)
        self.assertEqual(len(d['data'][6]), 10)
        self.assertEqual(len(d['data'][7]), 1)


class DividHTMLtable2dict(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.s = BoerseScraper(*dummy)
        cls.s._requestURL = MagicMock(return_value=bytes(DIVID_DATA, 'utf-8'))
        cls.tabs = cls.s._getHTMLTables(['Dividenden'], 'url')

    def test_defaultConversion(self):
        d = self.s._htmlTab2dict(self.tabs['Dividenden'])
        self.assertEqual(set(d.keys()), set(['colnames', 'rownames', 'data']))
        self.assertEqual(d['colnames'], [b'Dividende', b'Ver\xc3\xa4nderung', b'Rendite'])
        self.assertEqual(len(d['rownames']), 22)
        self.assertEqual(d['rownames'][0], b'12.05.17')
        self.assertEqual(d['rownames'][21], b'31.05.96')
        self.assertEqual(len(d['data']), 22)
        self.assertEqual(len(d['data'][0]), 3)
        self.assertEqual(len(d['data'][21]), 3)
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

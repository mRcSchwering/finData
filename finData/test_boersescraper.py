# This Python file uses the following encoding: utf-8
from finData.boersescraper import BoerseScraper
from finData.testing_utils import *
import datetime as dt
import numpy as np

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
        d = self.s._htmlTab2dict(self.tabs['Dividenden'], hasRownames=False)
        self.assertEqual(set(d.keys()), set(['colnames', 'data']))
        self.assertEqual(d['colnames'], [b'Datum', b'Dividende', b'Ver\xc3\xa4nderung', b'Rendite'])
        self.assertEqual(len(d['data']), 22)
        self.assertEqual(len(d['data'][0]), 4)
        self.assertEqual(len(d['data'][21]), 4)


class DecodeObjects(unittest.TestCase):

    def setUp(self):
        self.b = [
            b'sth',
            {
                'a': ['asd', b'asd', 1],
                'b': b'asd'
            },
            [b'a', b'b', b'c', {'x': b'y'}]
        ]
        self.s = BoerseScraper(*dummy)

    def test_correctlyDecodedDummy(self):
        act = self.s._decode(self.b)
        self.assertEqual(type(act[0]).__name__, 'str')
        self.assertEqual(type(act[1]['b']).__name__, 'str')
        self.assertEqual(type(act[1]['a'][0]).__name__, 'str')
        self.assertEqual(type(act[1]['a'][1]).__name__, 'str')
        self.assertEqual(type(act[1]['a'][2]).__name__, 'int')
        self.assertEqual(type(act[2][0]).__name__, 'str')
        self.assertEqual(type(act[2][1]).__name__, 'str')
        self.assertEqual(type(act[2][2]).__name__, 'str')
        self.assertEqual(type(act[2][3]['x']).__name__, 'str')


class GuessTypes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test = {
            'colnames': ['123', 'asd', '1.34'],
            'rownames': ['13.03.1990', '1.34', 'asd'],
            'data': [
                ['2009', '2010', '10.05.2011', '10.05.11'],
                ['10.000', '12,37%', '13%', 'n.v.'],
                ['287,00', '2.307,00', '0,00', '-%'],
                ['287,00', '2.307,00', '0,00', '']
            ]
        }
        s = BoerseScraper(*dummy)
        cls.res = s._guessTypes(test)

    def test_stringListsCorrect(self):
        for col in self.res['colnames']:
            self.assertEqual(type(col).__name__, 'str')
        for row in self.res['rownames']:
            self.assertEqual(type(row).__name__, 'str')

    def test_datesCorrect(self):
        self.assertEqual(self.res['data'][0][2], dt.date(2011, 5, 10))
        self.assertEqual(self.res['data'][0][3], dt.date(2011, 5, 10))

    def test_percentilesCorrect(self):
        self.assertAlmostEqual(self.res['data'][1][1], 0.1237)
        self.assertAlmostEqual(self.res['data'][1][2], 0.13)

    def test_NaNsCorrect(self):
        self.assertTrue(np.isnan(self.res['data'][1][3]))
        self.assertTrue(np.isnan(self.res['data'][2][3]))
        self.assertTrue(np.isnan(self.res['data'][3][3]))

    def test_numericsCorrect(self):
        self.assertAlmostEqual(self.res['data'][1][0], 10000)
        self.assertAlmostEqual(self.res['data'][2][0], 287)
        self.assertAlmostEqual(self.res['data'][2][1], 2307)
        self.assertAlmostEqual(self.res['data'][2][2], 0)
        self.assertAlmostEqual(self.res['data'][3][0], 287)
        self.assertAlmostEqual(self.res['data'][3][1], 2307)
        self.assertAlmostEqual(self.res['data'][3][2], 0)

    def test_integersCorrect(self):
        self.assertEqual(self.res['data'][0][0], 2009)
        self.assertEqual(type(self.res['data'][0][0]).__name__, 'int')
        self.assertEqual(self.res['data'][0][1], 2010)
        self.assertEqual(type(self.res['data'][0][1]).__name__, 'int')


class Table2DataFrameDefaults(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test = {
            'colnames': ['col3', 'col2', 'col1', 'col4', 'col5'],
            'rownames': ['row1', 'row2', 'row3'],
            'data': [
                [2009, 1.12, '1', dt.date(2010, 1, 1), ''],
                [2010, 2.00, '2', dt.date(2010, 1, 1), ''],
                [2011, 0.03, '3', dt.date(2010, 1, 1), '']
            ]
        }
        mapping = [
            {'from': 'col1', 'to': 'Col3', 'type': 'int'},
            {'from': 'col2', 'to': 'Col2', 'type': 'num'},
            {'from': 'col3', 'to': 'Col1', 'type': 'str'},
            {'from': 'col4', 'to': 'Col4', 'type': 'other'}
        ]
        s = BoerseScraper(*dummy)
        cls.res = s._table2DataFrame(test, mapping)

    def test_correctShape(self):
        self.assertEqual(self.res.shape[0], 3)
        self.assertEqual(self.res.shape[1], 4)

    def test_correctTypes(self):
        self.assertEqual(self.res['Col3'].dtype.name, 'int64')
        self.assertEqual(self.res['Col2'].dtype.name, 'float64')
        self.assertEqual(self.res['Col1'].dtype.name, 'object')
        self.assertEqual(self.res['Col4'].dtype.name, 'object')

    def test_correctColnames(self):
        exp = ['Col3', 'Col2', 'Col1', 'Col4']
        self.assertEqual(self.res.columns.tolist(), exp)


class ConcatNormalTables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tables = {
            'tab1': {
                'colnames': ['c1', 'c2'],
                'rownames': ['r1', 'r2'],
                'data': [['11', '12'], ['21', '22']]
            },
            'tab2': {
                'colnames': ['c1', 'c2'],
                'rownames': ['r3', 'r4'],
                'data': [['31', '32'], ['41', '42']]
            }
        }
        s = BoerseScraper(*dummy)
        cls.res = s._concatTables(cls.tables)

    def test_correctRownames(self):
        rownames = self.tables['tab1']['rownames'] + self.tables['tab2']['rownames']
        self.assertSetEqual(set(self.res['rownames']), set(rownames))

    def test_correctColnames(self):
        self.assertEqual(self.res['colnames'], self.tables['tab1']['colnames'])

    def test_rownamesCorrespondToData(self):
        i1 = self.res['rownames'].index('r1')
        i2 = self.res['rownames'].index('r2')
        i3 = self.res['rownames'].index('r3')
        i4 = self.res['rownames'].index('r4')
        self.assertEqual(self.res['data'][i1], ['11', '12'])
        self.assertEqual(self.res['data'][i2], ['21', '22'])
        self.assertEqual(self.res['data'][i3], ['31', '32'])
        self.assertEqual(self.res['data'][i4], ['41', '42'])


class ConcatTablesFailures(unittest.TestCase):

    def test_unequalColnames(self):
        tables = {
            'tab1': {
                'colnames': ['c1', 'c2'],
                'rownames': ['r1', 'r2'],
                'data': [['11', '12'], ['21', '22']]
            },
            'tab2': {
                'colnames': ['c1', 'c3'],
                'rownames': ['r3', 'r4'],
                'data': [['31', '32'], ['41', '42']]
            }
        }
        s = BoerseScraper(*dummy)
        with self.assertRaises(AttributeError):
                s._concatTables(tables)

    def test_duplicateRownames(self):
        tables = {
            'tab1': {
                'colnames': ['c1', 'c2'],
                'rownames': ['r1', 'r1'],
                'data': [['11', '12'], ['21', '22']]
            },
            'tab2': {
                'colnames': ['c1', 'c3'],
                'rownames': ['r3', 'r4'],
                'data': [['31', '32'], ['41', '42']]
            }
        }
        s = BoerseScraper(*dummy)
        with self.assertRaises(AttributeError):
                s._concatTables(tables)

    def test_rowAndRownamesLengthDiffer(self):
        tables = {
            'tab1': {
                'colnames': ['c1', 'c2'],
                'rownames': ['r1', 'r2', 'r3'],
                'data': [['11', '12'], ['21', '22']]
            },
            'tab2': {
                'colnames': ['c1', 'c3'],
                'rownames': ['r4'],
                'data': [['31', '32'], ['41', '42']]
            }
        }
        s = BoerseScraper(*dummy)
        with self.assertRaises(AttributeError):
                s._concatTables(tables)


class Table2DataFrameSpecialCases(unittest.TestCase):

    def test_transposeTable(self):
        test = {
            'colnames': ['col1', 'col2'],
            'rownames': ['row1', 'row2', 'row3'],
            'data': [
                [2009, 2010],
                [1.11, 2.22],
                [1, 2]
            ]
        }
        mapping = [
            {'from': 'row1', 'to': 'Row1', 'type': 'int'},
            {'from': 'row2', 'to': 'Row2', 'type': 'num'},
            {'from': 'row3', 'to': 'Row3', 'type': 'str'}
        ]
        s = BoerseScraper(*dummy)
        res = s._table2DataFrame(test, mapping, transpose=True)
        self.assertEqual(res.columns.tolist(), ['Row1', 'Row2', 'Row3'])
        self.assertEqual(res['Row1'].tolist(), [2009, 2010])
        self.assertEqual(res['Row2'].tolist(), [1.11, 2.22])
        self.assertEqual(res['Row3'].tolist(), ['1.0', '2.0'])
        self.assertEqual(res.index.tolist(), ['col1', 'col2'])

    def test_noRownames(self):
        test = {
            'colnames': ['col1', 'col2'],
            'data': [
                [2009, 1.11],
                [2010, 2.22]
            ]
        }
        mapping = [
            {'from': 'col1', 'to': 'Col1', 'type': 'int'},
            {'from': 'col2', 'to': 'Col2', 'type': 'num'}
        ]
        s = BoerseScraper(*dummy)
        res = s._table2DataFrame(test, mapping)
        self.assertEqual(res.columns.tolist(), ['Col1', 'Col2'])
        self.assertEqual(res['Col1'].tolist(), [2009, 2010])
        self.assertEqual(res['Col2'].tolist(), [1.11, 2.22])
        self.assertEqual(res.index.tolist(), [0, 1])

    def test_transposeAndNoColnames(self):
        test = {
            'rownames': ['row1', 'row2'],
            'data': [
                [2009, 2010],
                [1.11, 2.22]
            ]
        }
        mapping = [
            {'from': 'row1', 'to': 'Row1', 'type': 'int'},
            {'from': 'row2', 'to': 'Row2', 'type': 'num'}
        ]
        s = BoerseScraper(*dummy)
        res = s._table2DataFrame(test, mapping, transpose=True)
        self.assertEqual(res.columns.tolist(), ['Row1', 'Row2'])
        self.assertEqual(res['Row1'].tolist(), [2009, 2010])
        self.assertEqual(res['Row2'].tolist(), [1.11, 2.22])
        self.assertEqual(res.index.tolist(), [0, 1])

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

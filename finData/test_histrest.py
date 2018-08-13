# This Python file uses the following encoding: utf-8
from finData.histrest import HistRest
from finData.testing_utils import *
import datetime as dt
import json


with open('finData/testdata/hist.json') as inf:
    TESTDATA = json.dumps(json.load(inf))


class Mocked(HistRest):

    def _configure_api(self):
        return 'api_key'

    def _GET(cls, url):
        cls._get_url = url
        res = MagicMock()
        res.status_code = 200
        res.content.decode = MagicMock(return_value=TESTDATA)
        return res


class HistRESTsetup(unittest.TestCase):

    def setUp(self):
        self.a = Mocked('ADS.DE', 10)

    def test_mockingWorks(self):
        self.assertEqual(self.a._key, 'api_key')
        self.assertEqual(type(self.a.columns).__name__, 'list')
        self.assertEqual(type(self.a.data).__name__, 'DataFrame')

    def test_correctRequest(self):
        url = self.a._get_url
        base, params = url.split('?')
        exp = 'https://www.alphavantage.co/query'
        self.assertEqual(base, exp)
        params = params.split('&')
        exp = ['apikey=api_key', 'outputsize=compact',
               'function=TIME_SERIES_DAILY_ADJUSTED', 'symbol=ADS.DE']
        self.assertSetEqual(set(params), set(exp))


class HistDataFrame(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        hist = Mocked('ADS.DE', 10)
        cls.df = hist.data

    def test_structureOfHistIsCorrect(self):
        self.assertEqual(self.df.shape, (9, 9))
        exp = ['open', 'high', 'low', 'close', 'adj_close', 'volume',
               'divid_amt', 'split_coef', 'datum']
        self.assertEqual(list(self.df), exp)
        self.assertEqual(type(self.df['datum'][0]).__name__, 'date')

    def test_sept2001valuesAreCorrect(self):
        row = self.df.loc[[d.year == 2001 and d.month == 11 for d in self.df['datum']]]
        self.assertEqual(row['datum'].values.tolist()[0], dt.date(2001, 11, 19))
        self.assertEqual(row['open'].values.tolist()[0], 18.425)
        self.assertEqual(row['close'].values.tolist()[0], 18.5875)
        self.assertEqual(row['adj_close'].values.tolist()[0], 12.7916)

    def test_july2011valuesAreCorrect(self):
        row = self.df.loc[[d.year == 2011 and d.month == 7 for d in self.df['datum']]]
        self.assertEqual(row['datum'].values.tolist()[0], dt.date(2011, 7, 22))
        self.assertEqual(row['open'].values.tolist()[0], 54.3)
        self.assertEqual(row['close'].values.tolist()[0], 54.96)
        self.assertEqual(row['adj_close'].values.tolist()[0], 49.8291)

    def test_feb2012valuesAreCorrect(self):
        row = self.df.loc[[d.year == 2012 and d.month == 2 for d in self.df['datum']]]
        self.assertEqual(row['datum'].values.tolist()[0], dt.date(2012, 2, 23))
        self.assertEqual(row['open'].values.tolist()[0], 58.52)
        self.assertEqual(row['close'].values.tolist()[0], 58.9)
        self.assertEqual(row['adj_close'].values.tolist()[0], 53.4012)

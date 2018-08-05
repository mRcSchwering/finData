# This Python file uses the following encoding: utf-8
from finData.dividscraper import DividScraper
from finData.testing_utils import *
import datetime as dt
import numpy as np


ADS = ['Adidas-Aktie', 'DE000A1EWWW0']
with open('finData/testdata/divid.html') as inf:
    TESTDATA = inf.read()


class MockedRequest(DividScraper):

    def _requestURL(self, url):
        return bytes(TESTDATA, 'utf-8')


class ScraperSetup(unittest.TestCase):

    def setUp(self):
        self.a = MockedRequest(*ADS)

    def test_URLCorreceltyResolved(self):
        exp = 'https://www.boerse.de/dividenden/Adidas-Aktie/DE000A1EWWW0'
        self.assertEqual(self.a._url, exp)


class DividendDataFrame(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dividend = MockedRequest(*ADS)
        cls.df = dividend.data

    def test_structureOfDividIsCorrect(self):
        self.assertEqual(self.df.shape, (22, 4))
        exp = ['datum', 'dividende', 'veraenderu', 'rendite']
        self.assertEqual(list(self.df), exp)
        types = [d.name for d in self.df.dtypes]
        self.assertEqual(types, ['object', 'float64', 'float64', 'float64'])
        self.assertEqual(type(self.df['datum'][0]).__name__, 'date')

    def test_year1996valuesAreCorrect(self):
        row = self.df.loc[[d.year == 1996 for d in self.df['datum']]]
        self.assertEqual(row['datum'].values.tolist()[0], dt.date(1996, 5, 31))
        self.assertAlmostEqual(row['dividende'].values.tolist()[0], 0.032)
        self.assertTrue(np.isnan(row['veraenderu'].values.tolist()[0]))
        self.assertAlmostEqual(row['rendite'].values.tolist()[0], 0.0019)

    def test_year2016valuesAreCorrect(self):
        row = self.df.loc[[d.year == 2016 for d in self.df['datum']]]
        self.assertEqual(row['datum'].values.tolist()[0], dt.date(2016, 5, 13))
        self.assertAlmostEqual(row['dividende'].values.tolist()[0], 1.6)
        self.assertAlmostEqual(row['veraenderu'].values.tolist()[0], 0.0667)
        self.assertTrue(np.isnan(row['rendite'].values.tolist()[0]))

    def test_year2010valuesAreCorrect(self):
        row = self.df.loc[[d.year == 2010 for d in self.df['datum']]]
        self.assertEqual(row['datum'].values.tolist()[0], dt.date(2010, 5, 7))
        self.assertAlmostEqual(row['dividende'].values.tolist()[0], 0.35)
        self.assertAlmostEqual(row['veraenderu'].values.tolist()[0], -0.3)
        self.assertAlmostEqual(row['rendite'].values.tolist()[0], 0.0071)

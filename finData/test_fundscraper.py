# This Python file uses the following encoding: utf-8
from finData.fundscraper import FundScraper
from finData.testing_utils import *
import datetime as dt
import numpy as np


ADS = ['Adidas-Aktie', 'DE000A1EWWW0']
with open('finData/testdata/fund.html') as inf:
    TESTDATA = inf.read()


class MockedRequest(FundScraper):

    def _requestURL(self, url):
        return bytes(TESTDATA, 'utf-8')


class ScraperSetup(unittest.TestCase):

    def setUp(self):
        self.a = MockedRequest(*ADS)

    def test_URLCorreceltyResolved(self):
        exp = 'https://www.boerse.de/fundamental-analyse/Adidas-Aktie/DE000A1EWWW0'
        self.assertEqual(self.a._url, exp)


class FundDataFrame(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        fund = MockedRequest(*ADS)
        cls.df = fund.data

    def test_structureOfFundIsCorrect(self):
        self.assertEqual(self.df.shape, (9, 35))
        nFloats = sum([d == 'float64' for d in self.df.dtypes])
        nInts = sum([d == 'int64' for d in self.df.dtypes])
        nOther = sum([d == 'object' for d in self.df.dtypes])
        self.assertEqual(nFloats, 34)
        self.assertEqual(nInts, 1)
        self.assertEqual(nOther, 0)
        self.assertEqual(self.df.index.tolist(), [str(d) for d in range(2009, 2018)])

    def test_ebitSamples(self):
        self.assertTrue(np.isnan(self.df.loc['2010', 'EBIT']))
        self.assertEqual(self.df.loc['2013', 'EBIT'], 1202)
        self.assertEqual(self.df.loc['2017', 'EBIT'], 2070)

    def test_eigenkapitaSamples(self):
        self.assertTrue(np.isnan(self.df.loc['2010', 'eigen_quote']))
        self.assertAlmostEqual(self.df.loc['2013', 'eigen_quote'], 0.4732)
        self.assertAlmostEqual(self.df.loc['2017', 'eigen_quote'], 0.4442)

    def test_kgvSamples(self):
        self.assertTrue(np.isnan(self.df.loc['2010', 'KGV']))
        self.assertEqual(self.df.loc['2013', 'KGV'], 24.6)
        self.assertEqual(self.df.loc['2017', 'KGV'], 30.8)

    def test_personalSamples(self):
        self.assertTrue(np.isnan(self.df.loc['2010', 'personal']))
        self.assertEqual(self.df.loc['2013', 'personal'], 49808)
        self.assertEqual(self.df.loc['2017', 'personal'], 56888)

    def test_marktkapitaSamples(self):
        self.assertTrue(np.isnan(self.df.loc['2010', 'zahl_aktien']))
        self.assertEqual(self.df.loc['2013', 'zahl_aktien'], 209.22 * 10**3)
        self.assertEqual(self.df.loc['2017', 'zahl_aktien'], 203.86 * 10**3)

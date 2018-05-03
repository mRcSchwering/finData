# This Python file uses the following encoding: utf-8
import unittest
import finData.scrape
import datetime
import math
import os
import pandas as pd

ads = ['Addidas AG', 'Aktie', 'A1EWWW', 'DE000A1EWWW0', 'EUR',
       'Adidas-Aktie', 'ADS.DE']
bion = ['BB Biotech', 'Aktie', 'A0NFN3', 'CH0038389992', 'CHF',
        'BB-Biotech-Aktie', 'BION.SW']
stockA = ['Test AG', 'Aktie', 'XXXXX', 'XXXXX', 'EUR', 'abc.de', 'XXX.XX', True]


class Constructor(unittest.TestCase):

    def setUp(self):
        self.a = finData.scrape.Scraper(*ads)
        self.b = finData.scrape.Scraper(*bion)

    def test_fundURLsCorreceltyResolved(self):
        self.assertEqual(self.a.fund_url, 'https://www.boerse.de/fundamental-analyse/Adidas-Aktie/DE000A1EWWW0')
        self.assertEqual(self.b.fund_url, 'https://www.boerse.de/fundamental-analyse/BB-Biotech-Aktie/CH0038389992')

    def test_dividURLsCorrectlyResolved(self):
        self.assertEqual(self.a.divid_url, 'https://www.boerse.de/dividenden/Adidas-Aktie/DE000A1EWWW0')
        self.assertEqual(self.b.divid_url, 'https://www.boerse.de/dividenden/BB-Biotech-Aktie/CH0038389992')


class AlphavantageAPIkey(unittest.TestCase):

    def test_keyInEnvironment(self):
        os.environ['ALPHAVANTAGE_API_KEY'] = "key"
        x = finData.scrape.Scraper(*ads)
        self.assertEqual(x.alphavantage_api_key, 'key')

    def test_noKeyAvailable(self):
        x = finData.scrape.Scraper(*ads)
        x.alphavantage_api_key = ''
        with self.assertRaises(KeyError):
            x._alphavantage_api("some_query")


class GetFundamentalTables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        class X(finData.scrape.Scraper):
            def _getTables(self, url):
                with open('finData/testdata/fund.html') as inf:
                    testdata = inf.read()
                return bytes(testdata, 'utf-8')
        cls.x = X(*stockA)
        cls.x.getFundamentalTables()

    def test_allTablesAreThere(self):
        self.assertCountEqual(GetFundamentalTables.x.existingTables,
                              ['guv', 'bilanz', 'kennza', 'rentab', 'person', 'marktk'])

    def test_structureOfGUVisCorrect(self):
        df = GetFundamentalTables.x.get('guv')
        self.assertEqual(list(df),
                         ['year', 'umsatz', 'bruttoergeb', 'EBIT', 'EBT', 'jahresueber', 'dividendena'])
        row = df.iloc[[0]].values.tolist()[0]
        self.assertEqual([type(d) for d in row], 7 * [float])
        self.assertEqual(df.shape, (9, 7))

    def test_structureOfBilanzIsCorrect(self):
        df = GetFundamentalTables.x.get('bilanz')
        self.assertEqual(list(df),
                         ['year', 'umlaufvermo', 'anlagevermo', 'sum_aktiva', 'kurzfr_verb', 'langfr_verb',
                         'gesamt_verb', 'eigenkapita', 'sum_passiva', 'eigen_quote', 'fremd_quote'])
        row = df.iloc[[0]].values.tolist()[0]
        self.assertEqual([type(d) for d in row], 11 * [float])
        self.assertEqual(df.shape, (9, 11))

    def test_structureOfKennzaIsCorrect(self):
        df = GetFundamentalTables.x.get('kennza')
        self.assertEqual(list(df),
                         ['year', 'gewinn_verw', 'gewinn_unvw', 'umsatz', 'buchwert', 'dividende', 'KGV', 'KBV', 'KUV'])
        row = df.iloc[[0]].values.tolist()[0]
        self.assertEqual([type(d) for d in row], 9 * [float])
        self.assertEqual(df.shape, (9, 9))
#
#
# class Test_getDividendTable(unittest.TestCase):
#
#     def setUp(self):
#         self.a = finData.scrape.Scraper(*stockA)
#
#
# class Test_getHistoricPrices(unittest.TestCase):
#
#     def setUp(self):
#         self.a = finData.scrape.Scraper(*stockA)
#
#
# class Test_get(unittest.TestCase):
#
#     def setUp(self):
#         self.a = finData.scrape.Scraper(*stockA)


if __name__ == '__main__':
    unittest.main()

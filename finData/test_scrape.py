# This Python file uses the following encoding: utf-8
import unittest
import finData.scrape
import datetime
import math
import os
import pandas as pd
import json

ads = ['Addidas AG', 'Aktie', 'A1EWWW', 'DE000A1EWWW0', 'EUR', 'Adidas-Aktie', 'ADS.DE']
bion = ['BB Biotech', 'Aktie', 'A0NFN3', 'CH0038389992', 'CHF', 'BB-Biotech-Aktie', 'BION.SW']
stock = ['Test AG', 'Aktie', 'XXXXX', 'XXXXX', 'EUR', 'abc.de', 'XXX.XX', True]


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
        cls.x = X(*stock)
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

    def test_certainGUVvaluesAreCorrect(self):
        df = GetFundamentalTables.x.get('guv')
        self.assertAlmostEqual(df['EBIT'].values.tolist()[0], 508)
        self.assertTrue(math.isnan(df['EBIT'].values.tolist()[1]))

    def test_structureOfBilanzIsCorrect(self):
        df = GetFundamentalTables.x.get('bilanz')
        self.assertEqual(list(df),
                         ['year', 'umlaufvermo', 'anlagevermo', 'sum_aktiva', 'kurzfr_verb', 'langfr_verb',
                         'gesamt_verb', 'eigenkapita', 'sum_passiva', 'eigen_quote', 'fremd_quote'])
        row = df.iloc[[0]].values.tolist()[0]
        self.assertEqual([type(d) for d in row], 11 * [float])
        self.assertEqual(df.shape, (9, 11))

    def test_certainBilanzValuesAreCorrect(self):
        df = GetFundamentalTables.x.get('bilanz')
        self.assertAlmostEqual(df['eigen_quote'].values.tolist()[0], 0.4249)
        self.assertTrue(math.isnan(df['eigen_quote'].values.tolist()[1]))

    def test_structureOfKennzaIsCorrect(self):
        df = GetFundamentalTables.x.get('kennza')
        self.assertEqual(list(df),
                         ['year', 'gewinn_verw', 'gewinn_unvw', 'umsatz', 'buchwert', 'dividende', 'KGV', 'KBV', 'KUV'])
        row = df.iloc[[0]].values.tolist()[0]
        self.assertEqual([type(d) for d in row], 9 * [float])
        self.assertEqual(df.shape, (9, 9))

    def test_certainKennzaValuesAreCorrect(self):
        df = GetFundamentalTables.x.get('kennza')
        self.assertAlmostEqual(df['KGV'].values.tolist()[0], 30.20)
        self.assertTrue(math.isnan(df['KGV'].values.tolist()[1]))

    def test_structureOfRentabIsCorrect(self):
        df = GetFundamentalTables.x.get('rentab')
        self.assertEqual(list(df),
                         ['year', 'umsatzren', 'eigenkapren', 'geskapren', 'dividren'])
        row = df.iloc[[0]].values.tolist()[0]
        self.assertEqual([type(d) for d in row], 5 * [float])
        self.assertEqual(df.shape, (9, 5))

    def test_certainRentabValuesAreCorrect(self):
        df = GetFundamentalTables.x.get('rentab')
        self.assertAlmostEqual(df['dividren'].values.tolist()[0], 0.0093)
        self.assertTrue(math.isnan(df['dividren'].values.tolist()[1]))

    def test_structureOfPersonIsCorrect(self):
        df = GetFundamentalTables.x.get('person')
        self.assertEqual(list(df),
                         ['year', 'personal', 'aufwand', 'umsatz', 'gewinn'])
        row = df.iloc[[0]].values.tolist()[0]
        self.assertEqual([type(d) for d in row], 5 * [float])
        self.assertEqual(df.shape, (9, 5))

    def test_certainPersonValuesAreCorrect(self):
        df = GetFundamentalTables.x.get('person')
        self.assertEqual(df['personal'].values.tolist()[0], 39596)
        self.assertTrue(math.isnan(df['personal'].values.tolist()[1]))

    def test_structureOfMarktkIsCorrect(self):
        df = GetFundamentalTables.x.get('marktk')
        self.assertEqual(list(df),
                         ['year', 'zahl_aktien', 'marktkapita'])
        row = df.iloc[[0]].values.tolist()[0]
        self.assertEqual([type(d) for d in row], 3 * [float])
        self.assertEqual(df.shape, (9, 3))

    def test_certainMarktkValuesAreCorrect(self):
        df = GetFundamentalTables.x.get('marktk')
        self.assertAlmostEqual(df['zahl_aktien'].values.tolist()[0], 209.20)
        self.assertTrue(math.isnan(df['zahl_aktien'].values.tolist()[1]))


class GetDividendTables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        class X(finData.scrape.Scraper):
            def _getTables(self, url):
                with open('finData/testdata/divid.html') as inf:
                    testdata = inf.read()
                return bytes(testdata, 'utf-8')
        cls.x = X(*stock)
        cls.x.getDividendTable()

    def test_structureOfDividIsCorrect(self):
        df = GetDividendTables.x.get('divid')
        self.assertEqual(list(df),
                         ['datum', 'dividende', 'veraenderu', 'rendite'])
        row = df.iloc[[0]].values.tolist()[0]
        self.assertEqual([type(d) for d in row], [datetime.date] + 3 * [float])
        self.assertEqual(df.shape, (22, 4))

    def test_certainDividValuesAreCorrect(self):
        df = GetDividendTables.x.get('divid')
        self.assertAlmostEqual(df['rendite'].values.tolist()[0], 0.0119)
        self.assertTrue(math.isnan(df['rendite'].values.tolist()[1]))


class GetHistTables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        class X(finData.scrape.Scraper):
            def _alphavantage_api(self, query):
                with open('finData/testdata/hist.json') as inf:
                    testdata = json.load(inf)
                return testdata
        cls.x = X(*stock)
        cls.x.getHistoricPrices()

    def test_structureOfHistIsCorrect(self):
        df = GetHistTables.x.get('hist')
        row = df.iloc[[0]].values.tolist()[0]
        self.assertEqual([type(d) for d in row], 8 * [float])
        self.assertNotIsInstance(datetime.datetime, type(df.index.values[0]))
        self.assertTrue(df.index.values[0] < df.index.values[1])

    def test_certainHistValuesAreCorrect(self):
        df = GetHistTables.x.get('hist')
        self.assertAlmostEqual(df['close'].values.tolist()[0], 18.5875)

# TODO start enddatum implementieren -> gucken was api supportet

#
#
# class Test_getDividendTable(unittest.TestCase):
#
#     def setUp(self):
#         self.a = finData.scrape.Scraper(*stock)
#
#
# class Test_getHistoricPrices(unittest.TestCase):
#
#     def setUp(self):
#         self.a = finData.scrape.Scraper(*stock)
#
#
# class Test_get(unittest.TestCase):
#
#     def setUp(self):
#         self.a = finData.scrape.Scraper(*stock)


if __name__ == '__main__':
    unittest.main()

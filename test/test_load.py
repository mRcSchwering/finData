import unittest
import finData.load
import datetime
import math


ads = ['Addidas AG', 'Aktie', 'A1EWWW', 'DE000A1EWWW0', 'EUR',
       'Adidas-Aktie', 'ADS.DE']
bion = ['BB Biotech', 'Aktie', 'A0NFN3', 'CH0038389992', 'CHF',
        'BB-Biotech-Aktie', 'BION.SW']


class Test_getFundamentalTables(unittest.TestCase):

    def setUp(self):
        self.a = finData.load.Loader(*ads)
        self.b = finData.load.Loader(*bion)

    def tearDown(self):
        pass

    def test_URLs(self):
        self.assertEqual(self.a.fund_url, 'https://www.boerse.de/fundamental-analyse/Adidas-Aktie/DE000A1EWWW0')
        self.assertEqual(self.b.fund_url, 'https://www.boerse.de/fundamental-analyse/BB-Biotech-Aktie/CH0038389992')

    def test_returningTables(self):
        resA = self.a.getFundamentalTables(True)
        self.assertEqual(resA, self.a.fund_tables)
        resB = self.b.getFundamentalTables(True)
        self.assertEqual(resB, self.b.fund_tables)

    def test_extractedValuesStockA(self):
        res = self.a.getFundamentalTables(True, ids=['guv'],
                                          texts=['Marktkapitalisierung'])
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res['marktk']['colnames']), 9)
        self.assertEqual(res['marktk']['rownames'],
                         ['Anzahl der Aktien', 'Marktkapitalisierung'])
        idx16 = res['marktk']['colnames'].index('2016')
        idx16marktk = list(map(lambda x: x[idx16], res['marktk']['data']))
        self.assertEqual(idx16marktk, [201.49, 30253.57])
        idx16guv = list(map(lambda x: x[idx16], res['guv']['data']))
        self.assertEqual(idx16guv, [19291, 9379, 1491, 1444, 1017, 403])

    def test_extractedValuesStockB(self):
        res = self.b.getFundamentalTables(True, ids=['bilanz'], texts=[])
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res['bilanz']['colnames']), 9)
        idx16 = res['bilanz']['colnames'].index('2016')
        for d in map(lambda x: x[idx16], res['bilanz']['data']):
            self.assertTrue(math.isnan(d))


class Test_getDividendTable(unittest.TestCase):

    def setUp(self):
        self.a = finData.load.Loader(*ads)
        self.b = finData.load.Loader(*bion)

    def tearDown(self):
        pass

    def test_URLs(self):
        self.assertEqual(self.a.divid_url, 'https://www.boerse.de/dividenden/Adidas-Aktie/DE000A1EWWW0')
        self.assertEqual(self.b.divid_url, 'https://www.boerse.de/dividenden/BB-Biotech-Aktie/CH0038389992')

    def test_returningTables(self):
        resA = self.a.getDividendTable(True)
        self.assertEqual(resA, self.a.divid_table)
        resB = self.b.getDividendTable(True)
        self.assertEqual(resB, self.b.divid_table)

    def test_extractedValuesStockA(self):
        res = self.a.getDividendTable(True)
        self.assertEqual(res['colnames'],
                         ['Datum', 'Dividende', 'Veränderung', 'Rendite'])
        #idx16 = [i for (i, d) in enumerate(map(lambda x: x[0], res['data'])) if d.year == 2016]
        idx16 = list(map(lambda x: x[0].year, res['data'])).index(2016)
        self.assertEqual(res['data'][idx16][0], datetime.date(2016, 5, 13))
        floats = res['data'][idx16][1:]
        expected = [1.6, 0.0667, 0.0107]
        for i in range(len(floats)):
            self.assertAlmostEqual(floats[i], expected[i])
        with self.assertRaises(KeyError):
            res['rownames']

    def test_extractedValuesStockB(self):
        res = self.b.getDividendTable(True)
        self.assertEqual(res['colnames'], ['Datum', 'Dividende', 'Veränderung', 'Rendite'])
        idx16 = [i for (i, d) in enumerate(map(lambda x: x[0], res['data'])) if d.year == 2016]
        self.assertEqual(res['data'][idx16[0]][0], datetime.date(2016, 3, 21))
        floats = res['data'][idx16[0]][1:]
        expected = [2.66, 0.209, 0.0516]
        for i in range(len(floats)):
            self.assertAlmostEqual(floats[i], expected[i])
        with self.assertRaises(KeyError):
            res['rownames']


class Test_alphavantageAPI(unittest.TestCase):

    def setUp(self):
        self.a = finData.load.Loader(*ads)
        self.b = finData.load.Loader(*bion)

    def tearDown(self):
        pass

    def test_HistoricPricesStockA(self):
        self.a.getHistoricPrices()
        hist = self.a.get('hist')
        colnames = ['1. open', '2. high', '3. low', '4. close',
                    '5. adjusted close', '6. volume', '7. dividend amount',
                    '8. split coefficient']
        self.assertEqual(hist['colnames'], colnames)
        lookup = datetime.date(2018, 3, 16)
        res = hist['data'][hist['rownames'].index(lookup)]
        exp = [193.95, 196.6, 192.8, 194.1, 194.1, 1866982]
        for i in range(len(exp)):
            self.assertAlmostEqual(exp[i], res[i])

    def test_HistoricPricesStockB(self):
        self.b.getHistoricPrices()
        hist = self.b.get('hist')
        self.assertEqual(hist['colnames'], colnames)
        lookup = datetime.date(2018, 3, 16)
        res = hist['data'][hist['rownames'].index(lookup)]
        exp = [68.3, 69.75, 68.3, 69.75, 69.75, 95306]
        for i in range(len(exp)):
            self.assertAlmostEqual(exp[i], res[i])


class Test_get(unittest.TestCase):

    def setUp(self):
        self.a = finData.load.Loader(*ads)

    def tearDown(self):
        pass

    def test_general(self):
        with self.assertRaises(ValueError):
            self.a.get('asd')
        with self.assertRaises(ValueError):
            self.a.get('guv')
        self.a.getFundamentalTables()
        self.assertEqual(self.a.get('guv'), self.a.fund_tables['guv'])


if __name__ == '__main__':
    unittest.main()

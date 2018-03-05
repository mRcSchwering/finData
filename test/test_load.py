import unittest
import finData.load


class Test_getFundamentalTables(unittest.TestCase):

    def setUp(self):
        self.a = finData.load.Loader('Addidas AG', 'Aktie', 'A1EWWW', 'DE000A1EWWW0', 'Adidas-Aktie')
        self.b = finData.load.Loader('BB Biotech', 'Aktie', 'A0NFN3', 'CH0038389992', 'BB-Biotech-Aktie')

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
        res = self.a.getFundamentalTables(True, ids = ['guv'], texts = ['Marktkapitalisierung'])
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res['marktk']['colnames']), 9)
        self.assertEqual(res['marktk']['rownames'], ['Anzahl der Aktien', 'Marktkapitalisierung'])
        idx16 = [i for (i, d) in enumerate(res['marktk']['colnames']) if d == '2016']
        idx16marktk = list(map(lambda x: x[idx16[0]], res['marktk']['data']))
        self.assertEqual(idx16marktk, [201.49, 30253.57])
        idx16guv = list(map(lambda x: x[idx16[0]], res['guv']['data']))
        self.assertEqual(idx16guv, [19291, 9379, 1491, 1444, 1017, 403])


    def test_extractedValuesStockB(self):
        res = self.b.getFundamentalTables(True, ids = ['bilanz'], texts = [])
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res['bilanz']['colnames']), 9)
        idx16 = [i for (i, d) in enumerate(res['bilanz']['colnames']) if d == '2016']
        idx16bilanz = list(map(lambda x: x[idx16[0]], res['bilanz']['data']))
        self.assertEqual(idx16bilanz, [float('NaN'), float('NaN'), float('NaN')])




class Test_getDividendTable(unittest.TestCase):

    def setUp(self):
        self.a = finData.load.Loader('Addidas AG', 'Aktie', 'A1EWWW', 'DE000A1EWWW0', 'Adidas-Aktie')
        self.b = finData.load.Loader('BB Biotech', 'Aktie', 'A0NFN3', 'CH0038389992', 'BB-Biotech-Aktie')

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
        self.assertEqual(res['colnames'], ['Datum', 'Dividende', 'Veränderung', 'Rendite'])
        idx16 = [i for (i, d) in enumerate(map(lambda x: x[0], res['data'])) if d.year == 2016]
        self.assertEqual(res['data'][idx16[0]], [datetime.date(2016, 5, 13), 1.6, 0.0667, 0.0107])
        with self.assertRaises(KeyError):
            res['rownames']


    def test_extractedValuesStockB(self):
        res = self.b.getDividendTable(True)
        self.assertEqual(res['colnames'], ['Datum', 'Dividende', 'Veränderung', 'Rendite'])
        idx16 = [i for (i, d) in enumerate(map(lambda x: x[0], res['data'])) if d.year == 2016]
        self.assertEqual(res['data'][idx16[0]], [datetime.date(2016, 3, 21), 2.66, 0.209, 0.0516])
        with self.assertRaises(KeyError):
            res['rownames']




class yahoo_api(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_HistoricPrices(self):
        # res = finData.load.HistoricPrices('ADS.DE')
        # self.assertEqual(res.keys(), Index([u'Open', u'High', u'Low', u'Close', u'Adj Close', u'Volume'], dtype='object'))
        # self.assertEqual(res['Close']['2018-01-02'], 167.149)
        pass

if __name__ == '__main__':
    unittest.main()

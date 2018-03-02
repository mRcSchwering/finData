import unittest
import finData.load


class scraping_boerse(unittest.TestCase):

    def setUp(self):
        self.a = finData.load.Loader('Addidas AG', 'Aktie', 'A1EWWW', 'DE000A1EWWW0', 'Adidas-Aktie')
        self.b = finData.load.Loader('BB Biotech', 'Aktie', 'A0NFN3', 'CH0038389992', 'BB-Biotech-Aktie')

    def tearDown(self):
        pass


    def test_getFundamentalTables(self):
        self.assertEqual(self.a.fund_url, 'https://www.boerse.de/fundamental-analyse/Adidas-Aktie/DE000A1EWWW0')
        res = self.a.getFundamentalTables(True, ids = ['guv'], texts = ['Marktkapitalisierung'])
        self.assertEqual(len(res['marktk']['colnames']), 9)
        decoded = [x.decode() for x in res['marktk']['rownames']]
        self.assertEqual(decoded, ['Anzahl der Aktien', 'Marktkapitalisierung'])
        idx16 = [i for (i, y) in enumerate(res['marktk']['colnames']) if y.decode() == '2016']
        decoded = [x.decode() for x in list(map(lambda x: x[idx16[0]], res['marktk']['data']))]
        self.assertEqual(decoded, ['201,49', '30.253,57'])
        decoded = [x.decoded() for x in list(map(lambda x: x[idx16[0]], res['guv']['data']))]
        self.assertEqual(decoded, ['19.291', '9.379', '1.491', '1.444', '1.017', '403,00'])
        self.assertEqual(self.b.fund_url, 'https://www.boerse.de/fundamental-analyse/BB-Biotech-Aktie/CH0038389992')
        self.b.getFundamentalTables()
        self.assertEqual(self.b.fund_table, self.b.getFundamentalTables(True))


    def test_DividendTable(self):
        self.assertEqual(self.a.divid_url, 'https://www.boerse.de/dividenden/Adidas-Aktie/DE000A1EWWW0')
        res = self.a.getDividendTable(True)
        decoded = [x.decoded() for x in res['colnames']]
        self.assertEqual(decoded, ['Datum', 'Dividende', 'Ver\xc3\xa4nderung', 'Rendite'])
        idx16 = [i for (i, d) in enumerate(map(lambda x: x[0], res['data'])) if d.decode() == '13.05.16']
        decoded = [x.decode() for x in res['data'][idx16[0]]]
        self.assertEqual(decoded, ['13.05.16', '1,60', '6,67%', '1,07%'])
        with self.assertRaises(KeyError):
            res['rownames']
        self.assertEqual(self.b.divid_url, 'https://www.boerse.de/dividenden/BB-Biotech-Aktie/CH0038389992')
        self.b.getDividendTable()
        self.assertEqual(self.b.divid_table, self.b.getDividendTable(True))


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

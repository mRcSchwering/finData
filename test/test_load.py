import unittest
import finData.load

class load_finData(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_htmlTab2dict(self):
        from bs4 import BeautifulSoup
        htmlTable = (u'<table><tbody>' +
                u'<tr><td>&nbsp;</td><td>2008</td><td>2009</td><td>2010</td><td>2011</td><td>2012</td></tr>' +
                u'<tr><td>Personal am Jahresende</td><td>38.982</td><td>39.596</td><td>42.541</td><td>46.824</td><td>46.306</td></tr>' +
                u'<tr><td>Gewinn je Mitarbeiter</td><td>16.469,14</td><td>6.187,49</td><td>13.328,32</td><td>13.091,58</td><td>11.359,22</td></tr>' +
                u'<tr><td colspan="10"><div><h3>Personal</h3><div>blablabla</div></div></td></tr>' +
                u'</tbody></table>')
        soup = BeautifulSoup(htmlTable, 'lxml')
        res = finData.load.htmlTab2dict(soup)
        self.assertEqual(res['colnames'], ['2008', '2009', '2010', '2011', '2012'])
        self.assertEqual(res['rownames'], ['Personal am Jahresende', 'Gewinn je Mitarbeiter'])
        self.assertEqual(res['data'][0], ['38.982', '39.596', '42.541', '46.824', '46.306'])
        with self.assertRaises(UserWarning):
            finData.load.htmlTab2dict(soup, hasRownames=False, removeEmpty=False)

    def test_FundamentalTables(self):
        url_chr = 'https://www.boerse.de/fundamental-analyse/Adidas-Aktie/DE000A1EWWW0'
        res = finData.load.FundamentalTables(url_chr, ids = ['guv'], texts = ['Marktkapitalisierung'])
        self.assertEqual(len(res['marktk']['colnames']), 9)
        self.assertEqual(res['marktk']['rownames'], ['Anzahl der Aktien', 'Marktkapitalisierung'])
        idx16 = [i for (i, y) in enumerate(res['marktk']['colnames']) if y == '2016']
        self.assertEqual(map(lambda x: x[idx16[0]], res['marktk']['data']), ['201,49', '30.253,57'])
        self.assertEqual(map(lambda x: x[idx16[0]], res['guv']['data']), ['19.291', '9.379', '1.491', '1.444', '1.017', '403,00'])


if __name__ == '__main__':
    unittest.main()

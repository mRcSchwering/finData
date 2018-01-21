import unittest
import finData.load

class load_finData(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_htmlTab2dict(self):
        htmlTable = (u'<table><tbody>' +
                u'<tr><td>&nbsp;</td><td>2008</td><td>2009</td><td>2010</td><td>2011</td><td>2012</td></tr>' +
                u'<tr><td>Personal am Jahresende</td><td>38.982</td><td>39.596</td><td>42.541</td><td>46.824</td><td>46.306</td></tr>' +
                u'<tr><td>Gewinn je Mitarbeiter</td><td>16.469,14</td><td>6.187,49</td><td>13.328,32</td><td>13.091,58</td><td>11.359,22</td></tr>' +
                u'<tr><td colspan="10"><div><h3>Personal</h3><div>blablabla</div></div></td></tr>' +
                u'</tbody></table>')
        res = finData.load.htmlTab2dict(BeautifulSoup(htmlTable))
        self.assertEqual(res['colnames'], ['2008', '2009', '2010', '2011', '2012'])
        self.assertEqual(res['rownames'], ['Personal am Jahresende', 'Gewinn je Mitarbeiter'])
        self.assertEqual(res['data'][0], ['38.982', '39.596', '42.541', '46.824', '46.306'])
        res = finData.load.htmlTab2dict(BeautifulSoup(htmlTable), hasRownames=False, removeEmpty=False)
        self.assertEqual(res['data'][2], ['Personalblablabla'])
        htmlTable2 = htmlTable[:150] + htmlTable[170:]
        self.assertRaises(UserWarning, findData.load.htmlTab2dict(BeautifulSoup(htmlTable2)))

if __name__ == '__main__':
    unittest.main()

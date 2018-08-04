# This Python file uses the following encoding: utf-8
from finData.dividscraper import DividScraper
from finData.testing_utils import *

ADS = ['Adidas-Aktie', 'DE000A1EWWW0']

with open('finData/testdata/divid.html') as inf:
    TESTDATA = inf.read()


class MockedRequest(DividScraper):

    def _requestURL(self, url):
        return bytes(TESTDATA, 'utf-8')


class ScraperSetup(unittest.TestCase):

    def setUp(self):
        self.a = MockedRequest(*ADS)

    def test_URLsCorreceltyResolved(self):
        exp = 'https://www.boerse.de/dividenden/Adidas-Aktie/DE000A1EWWW0'
        self.assertEqual(self.a._url, exp)

    def test_HTMLtableFound(self):
        self.assertEqual(len(self.a._html_table), 46)
        self.assertEqual(type(self.a._html_table).__name__, 'Tag')


#
# class GetDividendTables(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         class X(finData.scrape.Scraper):
#             def _getTables(self, url):
#                 with open('finData/testdata/divid.html') as inf:
#                     testdata = inf.read()
#                 return bytes(testdata, 'utf-8')
#         cls.x = X(*stock)
#         cls.x.getDividendTable()
#
#     def test_structureOfDividIsCorrect(self):
#         df = GetDividendTables.x.get('divid')
#         self.assertEqual(list(df),
#                          ['datum', 'dividende', 'veraenderu', 'rendite'])
#         row = df.iloc[[0]].values.tolist()[0]
#         self.assertEqual([type(d) for d in row], [datetime.date] + 3 * [float])
#         self.assertEqual(df.shape, (22, 4))
#
#     def test_ascendingYearsInDivid(self):
#         df = GetDividendTables.x.get('divid')
#         lastYear = 0
#         for datum in df['datum']:
#             self.assertGreater(datum.year - lastYear, 0)
#             lastYear = datum.year
#
#     def test_certainDividValuesAreCorrect(self):
#         df = GetDividendTables.x.get('divid')
#         self.assertTrue(df['rendite'].values.tolist()[20])
#         self.assertTrue(df['veraenderu'].values.tolist()[0])
#         self.assertAlmostEqual(df['rendite'].values.tolist()[0], 0.0019)

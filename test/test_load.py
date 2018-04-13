# This Python file uses the following encoding: utf-8
import unittest
import finData.load


# TODO
# test psycopg2 mit unittest.mock
# https://gist.github.com/graphaelli/906b624c18f77f50da5cd0cd4211c3c8
# https://stackoverflow.com/questions/35143055/how-to-mock-psycopg2-cursor-object

# import datetime
# import math
#
# ads = ['Addidas AG', 'Aktie', 'A1EWWW', 'DE000A1EWWW0', 'EUR',
#        'Adidas-Aktie', 'ADS.DE']
# bion = ['BB Biotech', 'Aktie', 'A0NFN3', 'CH0038389992', 'CHF',
#         'BB-Biotech-Aktie', 'BION.SW']
# stockA = ['Test AG', 'Aktie', 'XXXXX', 'XXXXX', 'EUR', 'abc.de', 'XXX.XX', True]

x = "asdf"


class Test_init(unittest.TestCase):

    def setUp(self):
        self.x = finData.load.Loader("asdf", True)

    def test_fundURLs(self):
        self.assertEqual(self.x.name, "asdf")
        self.assertTrue(self.x.isTest)


if __name__ == '__main__':
    unittest.main()

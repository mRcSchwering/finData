# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs
from unittest.mock import patch
import finData.connect
import psycopg2 as pg
import unittest


conn_list = ['findata', 'testdb', 'postgres', '127.0.0.1', 5432]


class Constructor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with patch('finData.connect.Connector') as mock_class:
            cls.x = mock_class.return_value
            cls.x.return_value = 'asdf'
            #cls.x = finData.connect.Connector(**conn_list)

    def test_throwingProperErrorsOnStart(self):
        print(Constructor.x())


if __name__ == '__main__':
    unittest.main()

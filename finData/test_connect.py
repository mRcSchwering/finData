# This Python file uses the following encoding: utf-8
import unittest
import finData.connect

constring = ['schemanem', 'dbname', 'user', 'host', 1234]


class Constructor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        class X(finData.connect.Connector):
            def _connect(self):
                return 'connected'
        cls.x = X(*constring)

    def test_throwingProperErrorsOnStart(self):
        with self.assertRaises(TypeError):
            finData.connect.Connector()
        self.assertEqual(self.x.conn, 'connected')

    def test_setTableRecognizesWrongTable(self):
        with self.assertRaises(ValueError):
            self.x.setTable('asdf')
        self.x.setTable('hist')
        self.assertEqual(self.x.table, 'hist')


if __name__ == '__main__':
    unittest.main()

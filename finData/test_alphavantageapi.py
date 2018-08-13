# This Python file uses the following encoding: utf-8
from finData.alphavantageapi import AlphavantagAPI
from finData.testing_utils import *
import pandas as pd
import json


def mockAPI(response):

    class MockedAPI(AlphavantagAPI):

        def _configure_api(cls):
            return 'some_api_key'

        def _GET(cls, url):
            return response

    return MockedAPI()


class AlphavantagAPIsetup(unittest.TestCase):

    def setUp(self):
        self.api = mockAPI('test')

    def test_mockingAPIkeyWorks(self):
        self.assertEqual(self.api._key, 'some_api_key')

    def test_mockingGetWorks(self):
        self.assertEqual(self.api._GET('asd'), 'test')


class Requesting(unittest.TestCase):

    def test_noDictGiven(self):
        api = mockAPI('test')
        with self.assertRaises(TypeError):
            api._request([])

    def test_optionalParamsNotGiven(self):
        api = mockAPI('test')
        with self.assertRaises(KeyError):
            api._request({})
        with self.assertRaises(KeyError):
            api._request({'function': ''})

    def test_return404(self):
        mock = MagicMock()
        mock.status_code = 404
        api = mockAPI(mock)
        with self.assertRaises(AttributeError):
            api._request({'function': '', 'symbol': ''})

    def test_noKeysInResponse(self):
        mock = MagicMock()
        mock.status_code = 200
        mock.content.decode = MagicMock(return_value='[]')
        api = mockAPI(mock)
        with self.assertRaises(AttributeError):
            api._request({'function': '', 'symbol': ''})

    def test_errorInResponse(self):
        mock = MagicMock()
        mock.status_code = 200
        mock.content.decode = MagicMock(return_value='{"Error Message": ""}')
        api = mockAPI(mock)
        with self.assertRaises(ValueError):
            api._request({'function': '', 'symbol': ''})

    def test_normalResponse(self):
        mock = MagicMock()
        mock.status_code = 200
        mock.content.decode = MagicMock(return_value='{"a": "test"}')
        api = mockAPI(mock)
        res = api._request({'function': '', 'symbol': ''})
        self.assertEqual(res['a'], 'test')


class Reshaping(unittest.TestCase):

    def setUp(self):
        self.api = mockAPI('test')

    def test_normalReshape(self):
        df = pd.DataFrame({'a': [1, 2, 3], 'b': ['a', 'b', 'c']})
        mapping = [
            {'from': 'a', 'to': 'A'},
            {'from': 'b', 'to': 'B'},
        ]
        res = self.api._reshape(df, mapping)
        self.assertEqual(res.columns.tolist(), ['A', 'B'])
        self.assertEqual(res['A'].values.tolist(), [1, 2, 3])
        self.assertEqual(res['B'].values.tolist(), ['a', 'b', 'c'])

    def test_columnGetsOmitted(self):
        df = pd.DataFrame({'a': [1, 2, 3], 'b': ['a', 'b', 'c'], 'c': [4, 5, 6]})
        mapping = [
            {'from': 'a', 'to': 'A'},
            {'from': 'b', 'to': 'B'},
        ]
        res = self.api._reshape(df, mapping)
        self.assertEqual(res.columns.tolist(), ['A', 'B'])
        self.assertEqual(res['A'].values.tolist(), [1, 2, 3])
        self.assertEqual(res['B'].values.tolist(), ['a', 'b', 'c'])

    def test_dataHasKeyMissing(self):
        df = pd.DataFrame({'a': [1, 2, 3]})
        mapping = [
            {'from': 'a', 'to': 'A'},
            {'from': 'b', 'to': 'B'},
        ]
        with self.assertRaises(KeyError):
            self.api._reshape(df, mapping)

# This Python file uses the following encoding: utf-8
import pandas as pd
import requests
import json


class AlphavantagAPI(object):

    _key = None
    _url = 'https://www.alphavantage.co/query'

    def __init__(self):
        self._key = self._configure_api()

    def _request(self, paramsDict):
        """
        GET request to alphaVantag REST API

        provide params as dict key: value
        API reference: www.alphavantage.co/documentation
        """
        if self._key == '':
            raise KeyError('Alpha Vantage API Key not defined')
        if not isinstance(paramsDict, dict):
            raise TypeError('Provide parameters as dictionary of key: value')
        paramsReq = ['function', 'symbol']
        paramsOpt = ['outputsize', 'datatype', 'interval']
        for param in paramsReq:
            if param not in paramsDict.keys():
                raise KeyError('Parameter required: %s' % param)
        params = ['apikey=%s' % self._key]
        for key in paramsDict:
            if key not in paramsOpt + paramsReq:
                raise KeyError('Unused parameter: %s' % key)
            params.append('%s=%s' % (key, paramsDict[key]))
        req = '{url}?{params}'.format(url=self._url, params='&'.join(params))
        res = self._GET(req)
        if res.status_code != 200:
            raise AttributeError('Alpha Vantage returned: %s' % res.status_code)
        content = json.loads(res.content.decode())
        try:
            contentKeys = content.keys()
        except AttributeError:
            raise AttributeError('Alpha Vantage returned empty content')
        if 'Error Message' in contentKeys:
            raise ValueError(content['Error Message'])
        return content

    @classmethod
    def _GET(cls, url):
        return requests.get(url)

    @classmethod
    def _configure_api(cls):
        """
        Set API key for alphaVantage REST API
        """
        key = ''
        try:
            key = os.environ['ALPHAVANTAGE_API_KEY']
        except KeyError:
            try:
                with open('config.json') as ouf:
                    configFile = json.load(ouf)
                key = configFile['ALPHAVANTAGE_API_KEY']
            except (FileNotFoundError, KeyError):
                pass
        return key

    @classmethod
    def _reshape(cls, df, mapping):
        """
        Convert DataFrame using a mapping

        Mapping is list of dicts with each 'from' and 'to'.
        DataFrame columns are renamed 'from', 'to'.

        Names not appearing in mapping are not included in dataframe.
        """
        old_colnames = [c['from'] for c in mapping]
        df = df[old_colnames]
        new_colnames = []
        for old in old_colnames:
            new = [c['to'] for c in mapping if c['from'] == old]
            new_colnames.append(new[0])
        df.columns = new_colnames
        return df

    @classmethod
    def getColumnConversions(cls, filename):
        with open(filename) as inf:
            obj = json.load(inf)
        return obj

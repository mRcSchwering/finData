# This Python file uses the following encoding: utf-8
import pandas as pd


class AlphavantagAPI(object):

    data = None
    _alphavantage_api_key = None

    def __init__(self):
        DBColumnConversions = self.getColumnConversions(self.conversions_filename)
        self.columns = DBColumnConversions['hist_daily']
        self._configure_api()
        self.data = self._getData()

    def _request(self, query):
        """
        mere request

        reference: www.alphavantage.co/documentation
        """
        if self._alphavantage_api_key == '':
            raise KeyError('Alpha Vantage API Key not defined')
        if not isinstance(query, dict):
            raise TypeError('Provide query as dictionary of key: value')
        paramsReq = ['function', 'symbol']
        paramsOpt = ['outputsize', 'datatype', 'interval']
        for param in paramsReq:
            if param not in query.keys():
                raise KeyError('Parameter required: %s' % param)
        querystrings = ['apikey=%s' % self._alphavantage_api_key]
        for key in query:
            if key not in paramsOpt + paramsReq:
                raise KeyError('Unused parameter: %s' % key)
            querystrings.append('%s=%s' % (key, query[key]))
        res = requests.get(Scraper.alphavantage_api + '?' +
                           '&'.join(querystrings))
        if res.status_code != 200:
            raise ValueError('Alpha Vantage returned: %s' % res.status_code)
        content = json.loads(res.content.decode())
        try:
            contentKeys = content.keys()
        except AttributeError:
            raise AttributeError('Alpha Vantage returned empty content')
        if 'Error Message' in contentKeys:
            raise ValueError(content['Error Message'])
        return content

    @classmethod
    def _configure_api(cls):
        """
        API key for alpha vantag REST API
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
    def _reshape(cls, data, mapping):
        """
        Shape dataframe for database
        """
        df = pd.DataFrame \
            .from_dict(data['Time Series (Daily)'], orient='index', dtype=float)
        df['datum'] = df.index
        newCols = []
        for idx in range(len(df.columns)):
            newCols.append([c['name'] for c in mapping if c['id'] == df.columns[idx]][0])
        df.columns = newCols
        df = df[[c['name'] for c in mapping]]
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df

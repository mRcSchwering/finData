"""Short Description.

Detailed Description
"""

#import pandas_datareader as pdr   # deprecated prd.get_data_yahoo ???
#import pandas_datareader.data as web # usable DataReader ???
#from tiingo import TiingoClient # useful??: No!

import os
import re
import datetime
import requests
from bs4 import BeautifulSoup

class Loader(object):
    host = 'www.boerse.de'
    fund_route = 'fundamental-analyse'
    divid_route = 'dividenden'
    alphavantage_api = 'https://www.alphavantage.co/query'


    def __init__(self, name, typ, wkn, isin, boerse_name):
        self.name = str(name)
        self.typ = str(typ)
        self.wkn = str(wkn)
        self.isin = str(isin)
        self.boerse_name = str(boerse_name)
        self.existingTables = []
        self._resolve_boerse_urls()
        self.alphavantage_api_key = self._configure_api()


    def getFundamentalTables(self, returnTables = False,
                             ids = ['guv', 'bilanz', 'kennzahlen', 'rentabilitaet', 'personal'],
                             texts = ['Marktkapitalisierung']):
        """Scrape fundamental data tables from boerse.de given h3 Ids or h3 text search strings"""
        tabDict = {}
        soup = BeautifulSoup(requests.get(self.fund_url).content, 'lxml')
        for id in ids:
            h3 = soup.find(lambda tag: tag.get('id') == id and tag.name == 'h3')
            try:
                tabDict[id.lower()[:6]] = h3.findNext('table')
            except AttributeError:
                print('Table %s was not found' % id)
        for text in texts:
            h3 = soup.find(lambda tag: text in tag.text and tag.name == 'h3')
            try:
                tabDict[text.lower()[:6]] = h3.findNext('table')
            except AttributeError:
                print('Table %s was not found' % text)
        out = {}
        for key, tab in tabDict.items():
            out[key] = self._htmlTab2dict(tab, hasRownames=True, hasColnames=True, removeEmpty=True)
        utab = self._decode(out)
        self.fund_tables = self._guessTypes(utab)
        self.existingTables.extend(self.fund_tables.keys())
        if returnTables:
            return self.fund_tables


    def getDividendTable(self, returnTable = False,
                         text = 'Dividenden'):
        """Scrape dividend table from boerse.de given a h3 text search string"""
        soup = BeautifulSoup(requests.get(self.divid_url).content, 'lxml')
        h3 = soup.find(lambda tag: text in tag.text and tag.name == 'h3')
        try:
            tab = h3.findNext('table')
        except AttributeError:
            print('Table %s not found' % text)
        btab = self._htmlTab2dict(tab, hasRownames=False)
        utab = self._decode(btab)
        self.divid_table = self._guessTypes(utab)
        self.existingTables.append('divid')
        if returnTable:
            return self.divid_table


    def get(self, key):
        keys = ['guv', 'bilanz', 'kennza', 'rentab', 'person', 'marktk', 'divid', 'hist']
        if key not in keys:
            raise ValueError('Invalid key, expect one of: %s' % keys)
        if key not in self.existingTables:
            raise ValueError('No data exists for this key, existing data: %s' % self.existingTables)
        if key == 'divid':
            return self.divid_table
        if key == 'hist':
            return self.hist_table
        return self.fund_tables[key]


    def _resolve_boerse_urls(self):
        pre = 'https://' + Loader.host
        post = self.boerse_name + '/' + self.isin
        self.fund_url = '/'.join([pre, Loader.fund_route, post])
        self.divid_url = '/'.join([pre, Loader.divid_route, post])


    def _configure_api(self):
        key = ''
        try:
            key = os.environ['ALPHAVANTAGE_API_KEY']
        except KeyError:
            pass
        try:
            key = json.load(open('config.json'))['ALPHAVANTAGE_API_KEY']
        except KeyError:
            pass
        return key


    def _htmlTab2dict(self, tab,
                      hasRownames = True,
                      hasColnames = True,
                      removeEmpty = True,
                      checkTable = True):
        """Return dict of lists from html table string"""
        rows = tab.findAll('tr')
        rownamesIdx = 0 if hasRownames else -1
        colnamesIdx = 0 if hasColnames else -1

        data = []
        nonEmptyRowIdxs = []
        for idx, row in enumerate(rows[(colnamesIdx+1):]):
            thisRow = []
            for col in row.findAll('td')[(rownamesIdx+1):]:
                text = col.text.replace(u'\xa0', u' ').encode('utf-8').strip()
                thisRow.append(text)
            if not removeEmpty or not all(d == '' for d in thisRow):
                data.append(thisRow)
                nonEmptyRowIdxs.append(idx + (colnamesIdx+1))
        out = {'data': data}

        if hasRownames:
            rownames = []
            for row in [rows[i] for i in nonEmptyRowIdxs]:
                text = row.find('td').text.replace(u'\xa0', u' ').encode('utf-8').strip()
                rownames.append(text)
            out['rownames'] = rownames

        if hasColnames:
            colnames = []
            tag = 'th' if len(rows[colnamesIdx].findAll('th')) > 0 else 'td'
            for col in rows[colnamesIdx].findAll(tag)[(rownamesIdx+1):]:
                text = col.text.replace(u'\xa0', u' ').encode('utf-8').strip()
                colnames.append(text)
            out['colnames'] = colnames

        if checkTable and len(out['data']) > 1:
            lens = [len(row) for row in out['data']]
            diffs = map(lambda x: x[0] - x[1], zip(lens, lens[1:] + [lens[0]]))
            if not all(d == 0 for d in diffs):
                raise UserWarning('Data rows do not all have the same lengths')
        return out


    def _decode(self, obj):
        if isinstance(obj, dict):
            for key in obj:
                obj[key] = self._decode(obj[key])
        elif isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = self._decode(obj[i])
        elif isinstance(obj, bytes):
            obj = obj.decode()
        return obj


    def _guessTypes(self, obj,
                    defStr = ['colnames', 'rownames'],
                    defNaN = ['n.v.', '', '%', '-', '-%'],
                    rePerc = '(^.*)%$',
                    reNum = '^-?[0-9.]*,[0-9][0-9]?$',
                    reDate = [{'re': '^[0-9]{2}.[0-9]{2}.[0-9]{2}$', 'fmt': '%d.%m.%y'}]):
        identified = True
        if isinstance(obj, dict):
            for key in obj:
                if key in defStr:
                    obj[key] = [str(d) for d in obj[key]]
                else:
                    obj[key] = self._guessTypes(obj[key])
        elif isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = self._guessTypes(obj[i])
        else:
            if obj in defNaN:
                obj = float('NaN')
            elif re.search(rePerc, obj):
                x = re.search(rePerc, obj).group(1).replace(',', '.')
                x = x.replace(".", "", x.count(".") -1)
                obj = float('NaN') if x in defNaN else float(x) / 100
            elif re.search(reNum, obj):
                x = obj.replace(',', '.')
                x = x.replace(".", "", x.count(".") -1)
                obj = float('NaN') if x in defNaN else float(x)
            else:
                pass
                identified = False
                for d in reDate:
                    if re.search(d['re'], obj):
                        obj = datetime.datetime.strptime(obj, d['fmt']).date()
                        identified = True
                        break
            if not identified:
                raise ValueError('Value not identified: ' + obj)
        return obj


    def _alphavantage_api(self, query):
        """Reference: www.alphavantage.co/documentation"""
        if self.alphavantage_api_key == '':
            raise KeyError('Alpha Vantage API Key not defined')
        if not isinstance(query, dict):
            raise TypeError('Provide query as dictionary of key: value')
        paramsReq = ['function', 'symbol']
        paramsOpt = ['outputsize', 'datatype', 'interval']
        for param in paramsReq:
            if not param in query.keys():
                raise KeyError('Parameter required: %s' % param)
        querystrings = ['apikey=%s' % self.alphavantage_api_key]
        for key in query:
            if key not in paramsOpt + paramsReq:
                raise KeyError('Unused parameter: %s' % key)
            querystrings.append('%s=%s' % (key, query[key]))
        res = requests.get(Loader.alphavantage_api + '?' + '&'.join(querystrings))
        if res.status_code != 200:
            raise ValueError('Alpha Vantage returned: %s' % res.status_code)
        return res


    def _convert_alphavantage(self, data,
                              dateFmt = '%Y-%m-%d'):
        content = json.loads(data.content.decode())['Time Series (Daily)']
        dates = list(content.keys())
        try:
            datetime.datetime.strptime(dates[0], dateFmt)
        except ValueError:
            raise ValueError('Unexpected date structure')
        rownames = [datetime.datetime.strptime(d, dateFmt) for d in dates]
        colnames = list(content[dates[0]].keys())
        rows = []
        for row in content:
            rows.append([float(row[k]) for k in row])
        return {'rownames': rownames, 'colnames': colnames, 'data': data}


    def getHistoricPrices(self, ticker, returnTable = False):
        query = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': ticker,
            'outputsize': 'full'
        }
        res = self._alphavantage_api(query)
        res = json.loads(res.content.decode())['Time Series (Daily)']
        self.hist_table = self._convert_alphavantage(res)
        self.existingTables.append('hist')
        if returnTable:
            return self.hist_table



a = Loader('Addidas AG', 'Aktie', 'A1EWWW', 'DE000A1EWWW0', 'Adidas-Aktie')
a.getDividendTable()
a.getFundamentalTables()
x = a.getHistoricPrices('ADS.DE')
x.status_code
y = json.loads(x.content.decode())
y.keys()
yy = y['Time Series (Daily)']
y['Meta Data']

# TODO get() für tables und listen welche tables es gibt

# TODO eigene API bauen!!
# ticker = "ADS"
# start = datetime.datetime(1990, 1, 1)
#
# def HistoricPrices(ticker,
#                    start = datetime.datetime(1990, 1, 1)):
#     """Download historic prices from yahoo! using ticker symbol"""
#     # koennte man auch scrapen (aber dann ohne adjusted Prices)
#     # Bsp: https://www.boerse.de/historische-kurse/BB-Biotech-Aktie/CH0038389992_seite,231,anzahl,20
#     return pdr.get_data_yahoo(ticker, start=start)
#     #return web.DataReader(ticker, "yahoo", start=start)
#
# x = pdr.get_data_yahoo(ticker, start=start)
#
# 'https://www.investopedia.com/markets/api/partial/historical/?Symbol=HMSF.L&Type=Historical+Prices&Timeframe=Daily&StartDate=Jan+10%2C+2018'
# 'https://www.investopedia.com/markets/api/partial/historical/?Symbol=ADS.DE&Type=Historical+Prices&Timeframe=Daily&StartDate=Jan+10%2C+2018'
# x

# testStock = [
#     {
#         'Name': 'Addidas AG',
#         'Typ': 'Aktie',
#         'WKN': 'A1EWWW',
#         'ISIN': 'DE000A1EWWW0',
#         'yahooTicker': 'ADS.DE',
#         'boerseURL': 'Adidas-Aktie/DE000A1EWWW0'
#     },
#     {
#         'Name': 'BB Biotech',
#         'Typ': 'Aktie',
#         'WKN': 'A0NFN3',
#         'ISIN': 'CH0038389992',
#         'yahooTicker': 'BBZA.DE',
#         'boerseURL': 'BB-Biotech-Aktie/CH0038389992'
#     }
# ]
# boerseDe = {
#     'host': 'www.boerse.de',
#     'pathFund': 'fundamental-analyse',
#     'pathDivid': 'dividenden'
# }
#
# Fund_url = 'https://%s/%s/%s' % (boerseDe['host'], boerseDe['pathFund'], testStock[1]['boerseURL'])
# Divid_url = 'https://%s/%s/%s' % (boerseDe['host'], boerseDe['pathDivid'], testStock[1]['boerseURL'])




def main():
    pass

"""Short Description.

Detailed Description
"""

#import pandas_datareader as pdr   # deprecated prd.get_data_yahoo ???
#import pandas_datareader.data as web # usable DataReader ???
#from tiingo import TiingoClient # useful??: No!

import os
import re
import json
import requests
import datetime as dt
from bs4 import BeautifulSoup


class Loader(object):
    host = 'www.boerse.de'
    fund_route = 'fundamental-analyse'
    divid_route = 'dividenden'
    alphavantage_api = 'https://www.alphavantage.co/query'
    currencies = ['EUR', 'CHF', 'USD', 'TWD', 'SGD', 'INR',
                  'CNY', 'JPY', 'KRW', 'RUB']
    tables = ['guv', 'bilanz', 'kennza', 'rentab', 'person',
              'marktk', 'divid', 'hist']

    def __init__(self, name, typ, wkn, isin, currency,
                 boerse_name, avan_ticker):
        self.name = str(name)
        self.typ = str(typ)
        self.wkn = str(wkn)
        self.isin = str(isin)
        self.currency = str(currency)
        if self.currency not in Loader.currencies:
            raise ValueError('Invalid currency ' +
                             'expect one of: %s' % Loader.currencies)
        self.boerse_name = str(boerse_name)
        self.avan_ticker = str(avan_ticker)
        self.existingTables = []
        self._resolve_boerse_urls()
        self.alphavantage_api_key = self._configure_api()

    def getFundamentalTables(self, returnTables=False,
                             ids=['guv', 'bilanz', 'kennzahlen',
                                  'rentabilitaet', 'personal'],
                             texts=['Marktkapitalisierung']):
        """Scrape fundamental data tables from boerse.de
        given h3 Ids or h3 text search strings"""
        tabDict = {}
        soup = BeautifulSoup(requests.get(self.fund_url).content, 'lxml')
        for id in ids:
            h3 = soup.find(
                lambda tag: tag.get('id') == id and tag.name == 'h3'
            )
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
            out[key] = self._htmlTab2dict(tab, hasRownames=True,
                                          hasColnames=True, removeEmpty=True)
        utab = self._decode(out)
        self.fund_tables = self._guessTypes(utab)
        self.existingTables.extend(self.fund_tables.keys())
        if returnTables:
            return self.fund_tables

    def getDividendTable(self, returnTable=False, text='Dividenden'):
        """Scrape dividend table from boerse.de
        given a h3 text search string"""
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
        """preferred way to access data of the object"""
        if key not in Loader.tables:
            raise ValueError('Invalid key, expect one of: %s' % Loader.tables)
        if key not in self.existingTables:
            raise ValueError('No data exists for this key' +
                             ' existing data: %s' % self.existingTables)
        if key == 'divid':
            return self.divid_table
        if key == 'hist':
            return self.hist_table
        return self.fund_tables[key]

    def _resolve_boerse_urls(self):
        """resolving URLs for boerse.de"""
        pre = 'https://' + Loader.host
        post = self.boerse_name + '/' + self.isin
        self.fund_url = '/'.join([pre, Loader.fund_route, post])
        self.divid_url = '/'.join([pre, Loader.divid_route, post])

    def _configure_api(self):
        """API key for alpha vantag REST API"""
        key = ''
        try:
            key = os.environ['ALPHAVANTAGE_API_KEY']
        except KeyError:
            pass
        if key != '':
            return key
        try:
            configFile = json.load(open('config.json'))
            try:
                key = configFile['ALPHAVANTAGE_API_KEY']
            except KeyError:
                pass
        except FileNotFoundError:
            pass
        return key

    def _htmlTab2dict(self, tab, hasRownames=True, hasColnames=True,
                      removeEmpty=True, checkTable=True):
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
                text = row.find('td') \
                    .text.replace(u'\xa0', u' ') \
                    .encode('utf-8').strip()
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

    def _guessTypes(self, obj, defStr=['colnames', 'rownames'],
                    defNaN=['n.v.', '', '%', '-', '-%'], rePerc='(^.*)%$',
                    reNum='^-?[0-9.]*,[0-9][0-9]?$',
                    reDate=[{'re': '^[0-9]{2}.[0-9]{2}.[0-9]{2}$',
                             'fmt': '%d.%m.%y'}]):
        """Guess and convert types for fundamental tables and dividend table"""
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
                x = x.replace(".", "", x.count(".") - 1)
                obj = float('NaN') if x in defNaN else float(x) / 100
            elif re.search(reNum, obj):
                x = obj.replace(',', '.')
                x = x.replace(".", "", x.count(".") - 1)
                obj = float('NaN') if x in defNaN else float(x)
            else:
                pass
                identified = False
                for d in reDate:
                    if re.search(d['re'], obj):
                        obj = dt.datetime.strptime(obj, d['fmt']).date()
                        identified = True
                        break
            if not identified:
                raise ValueError('Value not identified: ' + obj)
        return obj

    def _alphavantage_api(self, query):
        """mere request; reference: www.alphavantage.co/documentation"""
        if self.alphavantage_api_key == '':
            raise KeyError('Alpha Vantage API Key not defined')
        if not isinstance(query, dict):
            raise TypeError('Provide query as dictionary of key: value')
        paramsReq = ['function', 'symbol']
        paramsOpt = ['outputsize', 'datatype', 'interval']
        for param in paramsReq:
            if param not in query.keys():
                raise KeyError('Parameter required: %s' % param)
        querystrings = ['apikey=%s' % self.alphavantage_api_key]
        for key in query:
            if key not in paramsOpt + paramsReq:
                raise KeyError('Unused parameter: %s' % key)
            querystrings.append('%s=%s' % (key, query[key]))
        res = requests.get(Loader.alphavantage_api + '?' +
                           '&'.join(querystrings))
        if res.status_code != 200:
            raise ValueError('Alpha Vantage returned: %s' % res.status_code)
        try:
            content = json.loads(res.content.decode()).keys()
        except AttributeError:
            raise AttributeError('Alpha Vantage returned empty content')
        if 'Error Message' in content:
            raise ValueError(json.loads(res.content.decode())['Error Message'])
        return res

    def _convert_alphavantage(self, data,
                              dateFmt='%Y-%m-%d'):
        """alphavantage REST to dict conversion"""
        content = json.loads(data.content.decode())['Time Series (Daily)']
        dates = sorted(list(content.keys()))
        try:
            dt.datetime.strptime(dates[0], dateFmt)
        except ValueError:
            raise ValueError('Unexpected date structure')
        rownames = [dt.datetime.strptime(d, dateFmt).date() for d in dates]
        colnames = sorted(list(content[dates[0]].keys()))
        rows = []
        for date in dates:
            row = content[date]
            rows.append([float(row[i]) for i in colnames])
        return {'rownames': rownames, 'colnames': colnames, 'data': rows}

    def getHistoricPrices(self, returnTable=False):
        query = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': self.avan_ticker,
            'outputsize': 'full'
        }
        res = self._alphavantage_api(query)
        self.hist_table = self._convert_alphavantage(res)
        self.existingTables.append('hist')
        if returnTable:
            return self.hist_table


# a = Loader('Addidas AG', 'Aktie', 'A1EWWW', 'DE000A1EWWW0', 'EUR', 'Adidas-Aktie', 'ADS.DE')
# a.getDividendTable()
# a.getFundamentalTables()
# a.getHistoricPrices()
#
# hist = a.get('hist')
# colnames = ['1. open', '2. high', '3. low', '4. close', '5. adjusted close',
#             '6. volume', '7. dividend amount', '8. split coefficient']
# colnames == hist['colnames']
#
# lookup = dt.datetime(2018, 3, 16)
# res = hist['data'][hist['rownames'].index(lookup.date())]
# exp = [193.95, 196.6, 192.8, 194.1, 194.1, 1866982]
# res[:6] == exp
#
#
# b = Loader('BB Biotech', 'Aktie', 'A0NFN3', 'CH0038389992', 'CHF', 'BB-Biotech-Aktie', 'BION.SW')
# b.getDividendTable()
# b.getFundamentalTables()
# b.getHistoricPrices()
#
# hist = b.get('hist')
# colnames = ['1. open', '2. high', '3. low', '4. close', '5. adjusted close',
#             '6. volume', '7. dividend amount', '8. split coefficient']
# colnames == hist['colnames']
#
# lookup = dt.datetime(2018, 3, 16)
# res = hist['data'][hist['rownames'].index(lookup.date())]
# exp = [68.3, 69.75, 68.3, 69.75, 69.75, 95306]
# res[:6] == exp


# TODO gucken welche Ticker die richtigen sind, notieren wie ich das raus kriege
# TODO Test schreiben für BBiotech und Adidas
# TODO gucken wie man adj close berechnet/ bzw ob ich den laufend weiter benutzen kann (kummulativ berechnet?)


def main():
    pass

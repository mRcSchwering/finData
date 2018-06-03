# This Python file uses the following encoding: utf-8
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
import os
import re
import json
import requests


class Scraper(object):
    """Data scraping from boerse.de and requesting from alphavantage.co"""

    host = 'www.boerse.de'
    fund_route = 'fundamental-analyse'
    divid_route = 'dividenden'
    alphavantage_api = 'https://www.alphavantage.co/query'
    currencies = ['EUR', 'CHF', 'USD', 'TWD', 'SGD', 'INR', 'CNY', 'JPY', 'KRW', 'RUB']
    tables = ['guv', 'bilanz', 'kennza', 'rentab', 'person', 'marktk', 'divid', 'hist']

    # column types as they will be in DB schema (rest is numeric)
    date_columns = ['datum']
    int_columns = ['year']

    # column id conversion to name as in DB schema for each table
    guv_id2name = [
        {'id': 'Umsatz', 'name': 'umsatz'},
        {'id': 'Bruttoergebnis', 'name': 'bruttoergeb'},
        {'id': 'Operatives Ergebnis (EBIT)', 'name': 'EBIT'},
        {'id': 'Ergebnis vor Steuer (EBT)', 'name': 'EBT'},
        {'id': 'Jahresüberschuss', 'name': 'jahresueber'},
        {'id': 'Dividendenausschüttung', 'name': 'dividendena'}
    ]
    bilanz_id2name = [
        {'id': 'Umlaufvermögen', 'name': 'umlaufvermo'},
        {'id': 'Anlagevermögen', 'name': 'anlagevermo'},
        {'id': 'Summe Aktiva', 'name': 'sum_aktiva'},
        {'id': 'Kurzfristige Verbindlichkeiten', 'name': 'kurzfr_verb'},
        {'id': 'Langfristige Verbindlichkeiten', 'name': 'langfr_verb'},
        {'id': 'Gesamtverbindlichkeiten', 'name': 'gesamt_verb'},
        {'id': 'Eigenkapital', 'name': 'eigenkapita'},
        {'id': 'Summe Passiva', 'name': 'sum_passiva'},
        {'id': 'Eigenkapitalquote', 'name': 'eigen_quote'},
        {'id': 'Fremdkapitalquote', 'name': 'fremd_quote'}
    ]
    rentab_id2name = [
        {'id': 'Umsatzrendite', 'name': 'umsatzren'},
        {'id': 'Eigenkapitalrendite', 'name': 'eigenkapren'},
        {'id': 'Gesamtkapitalrendite', 'name': 'geskapren'},
        {'id': 'Dividendenrendite', 'name': 'dividren'}
    ]
    person_id2name = [
        {'id': 'Personal am Jahresende', 'name': 'personal'},
        {'id': 'Personalaufwand in Mio.', 'name': 'aufwand'},
        {'id': 'Umsatz je Mitarbeiter', 'name': 'umsatz'},
        {'id': 'Gewinn je Mitarbeiter', 'name': 'gewinn'}
    ]
    marktk_id2name = [
        {'id': 'Anzahl der Aktien', 'name': 'zahl_aktien'},
        {'id': 'Marktkapitalisierung', 'name': 'marktkapita'}
    ]
    kennza_id2name = [
        {'id': 'Gewinn je Aktie (verwässert)', 'name': 'gewinn_verw'},
        {'id': 'Gewinn je Aktie (unverwässert)', 'name': 'gewinn_unvw'},
        {'id': 'Umsatz je Aktie', 'name': 'umsatz'},
        {'id': 'Buchwert je Aktie', 'name': 'buchwert'},
        {'id': 'Dividende je Aktie', 'name': 'dividende'},
        {'id': 'KGV (Kurs-Gewinn-Verhältnis)', 'name': 'KGV'},
        {'id': 'KBV (Kurs-Buchwert-Verhältnis)', 'name': 'KBV'},
        {'id': 'KUV (Kurs-Umsatz-Verhältnis)', 'name': 'KUV'}
    ]
    divid_id2name = [
        {'id': 'Datum', 'name': 'datum'},
        {'id': 'Dividende', 'name': 'dividende'},
        {'id': 'Veränderung', 'name': 'veraenderu'},
        {'id': 'Rendite', 'name': 'rendite'}
    ]
    hist_id2name = [
        {'id': 'datum', 'name': 'datum'},
        {'id': '1. open', 'name': 'open'},
        {'id': '2. high', 'name': 'high'},
        {'id': '3. low', 'name': 'low'},
        {'id': '4. close', 'name': 'close'},
        {'id': '5. adjusted close', 'name': 'adj_close'},
        {'id': '6. volume', 'name': 'volume'},
        {'id': '7. dividend amount', 'name': 'divid_amt'},
        {'id': '8. split coefficient', 'name': 'split_coef'}
    ]

    def __init__(self, name, typ, wkn, isin, currency,
                 boerse_name, avan_ticker):
        self.name = str(name)
        self.typ = str(typ)
        self.wkn = str(wkn)
        self.isin = str(isin)
        self.currency = str(currency)
        if self.currency not in Scraper.currencies:
            raise ValueError('Invalid currency ' +
                             'expect one of: %s' % Scraper.currencies)
        self.boerse_name = str(boerse_name)
        self.avan_ticker = str(avan_ticker)
        self.existingTables = []
        self._resolve_boerse_urls()
        self.alphavantage_api_key = Scraper._configure_api()

    def getFundamentalTables(self,
                             ids=['guv', 'bilanz', 'kennzahlen', 'rentabilitaet', 'personal'],
                             texts=['Marktkapitalisierung']):
        """Scrape fundamental data tables from boerse.de given h3 Ids or h3 text search strings"""
        tabDict = {}
        req = self._getTables(self.fund_url)
        soup = BeautifulSoup(req, 'lxml')

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
            out[key] = Scraper._htmlTab2dict(tab, hasRownames=True, hasColnames=True, removeEmpty=True)
        utab = Scraper._decode(out)
        self.fund_tables = Scraper._guessTypes(utab)
        self.existingTables.extend(self.fund_tables.keys())

    def getDividendTable(self, text='Dividenden'):
        """Scrape dividend table from boerse.de given a h3 text search string"""
        req = self._getTables(self.divid_url)
        soup = BeautifulSoup(req, 'lxml')
        h3 = soup.find(lambda tag: text in tag.text and tag.name == 'h3')
        try:
            tab = h3.findNext('table')
        except AttributeError:
            print('Table %s not found' % text)
        btab = Scraper._htmlTab2dict(tab, hasRownames=False)
        utab = Scraper._decode(btab)
        self.divid_table = Scraper._guessTypes(utab)
        self.existingTables.append('divid')

    def getHistoricPrices(self, onlyLast100=False):
        """Use alphavantage API to request historic prices"""
        query = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': self.avan_ticker,
            'outputsize': 'compact' if onlyLast100 else 'full'
        }
        self.hist_table = self._alphavantage_api(query)
        self.existingTables.append('hist')

    def get(self, key):
        """Return table as pd.DataFrame"""
        if key not in Scraper.tables:
            raise ValueError('Invalid key, expect one of: %s' % Scraper.tables)
        if key not in self.existingTables:
            raise ValueError('No data exists for this key' +
                             ' existing data: %s' % self.existingTables)
        options = {
            'guv': lambda: Scraper._toDataFrame(self.fund_tables[key], Scraper.guv_id2name),
            'bilanz': lambda: Scraper._toDataFrame(self.fund_tables[key], Scraper.bilanz_id2name),
            'rentab': lambda: Scraper._toDataFrame(self.fund_tables[key], Scraper.rentab_id2name),
            'person': lambda: Scraper._toDataFrame(self.fund_tables[key], Scraper.person_id2name),
            'marktk': lambda: Scraper._toDataFrame(self.fund_tables[key], Scraper.marktk_id2name),
            'kennza': lambda: Scraper._toDataFrame(self.fund_tables[key], Scraper.kennza_id2name),
            'divid': lambda: Scraper._toDataFrame(self.divid_table, Scraper.divid_id2name, typ='divid'),
            'hist': lambda: Scraper._toDataFrame(self.hist_table, Scraper.hist_id2name, typ='hist')
        }
        return options[key]()

    def _resolve_boerse_urls(self):
        """resolving URLs for boerse.de"""
        pre = 'https://' + Scraper.host
        post = self.boerse_name + '/' + self.isin
        self.fund_url = '/'.join([pre, Scraper.fund_route, post])
        self.divid_url = '/'.join([pre, Scraper.divid_route, post])

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

    def _getTables(cls, url):
        """Request url for html"""
        return requests.get(url).content

    @classmethod
    def _guessTypes(cls, obj, defStr=['colnames', 'rownames'],
                    defNaN=['n.v.', '', '%', '-', '-%'], rePerc='(^.*)%$',
                    reNum='^-?[0-9.]*,[0-9][0-9]*$',
                    reDate=[{'re': '^[0-9]{2}.[0-9]{2}.[0-9]{2}$',
                             'fmt': '%d.%m.%y'}]):
        """Guess and convert types for fundamental tables and dividend table"""
        identified = True
        if isinstance(obj, dict):
            for key in obj:
                if key in defStr:
                    obj[key] = [str(d) for d in obj[key]]
                else:
                    obj[key] = cls._guessTypes(obj[key])
        elif isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = cls._guessTypes(obj[i])
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

    @classmethod
    def _decode(cls, obj):
        """Recursive decoding of objects"""
        if isinstance(obj, dict):
            for key in obj:
                obj[key] = cls._decode(obj[key])
        elif isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = cls._decode(obj[i])
        elif isinstance(obj, bytes):
            obj = obj.decode()
        return obj

    @classmethod
    def _configure_api(cls):
        """API key for alpha vantag REST API"""
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
    def _htmlTab2dict(cls, tab, hasRownames=True, hasColnames=True,
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

    @classmethod
    def _toDataFrame(cls, data, mapping, typ='fund'):
        """Convert tables as from _htmlTab2dict into pd.DataFrames as in DB schema"""
        if typ == 'fund':
            tmp = {'year': [d for d in data['colnames']]}
            for col in mapping:
                if col['id'] in data['rownames']:
                    idx = data['rownames'].index(col['id'])
                    tmp[col['name']] = data['data'][idx]
                else:
                    tmp[col['name']] = len(data['colnames']) * [float('NaN')]
            df = pd.DataFrame.from_dict(tmp)
            df = df[['year'] + [c['name'] for c in mapping]]
            df.sort_values(by='year', inplace=True)

        if typ == 'divid':
            tmp = {}
            for col in mapping:
                if col['id'] in data['colnames']:
                    idx = data['colnames'].index(col['id'])
                    tmp[col['name']] = [d[idx] for d in data['data']]
                else:
                    tmp[col['name']] = len(data['data']) * [float('NaN')]
            df = pd.DataFrame.from_dict(tmp)
            df = df[[c['name'] for c in mapping]]
            df['datum'] = pd.to_datetime(df['datum'])
            df.sort_values(by='datum', inplace=True)

        if typ == 'hist':
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

        dateCols = [c for c in df.columns if c in cls.date_columns]
        intCols = [c for c in df.columns if c in cls.int_columns]
        numCols = [c for c in df.columns if c not in dateCols + intCols]
        df[dateCols] = df[dateCols].astype('datetime64[ns]')
        for col in dateCols:
            df[col] = [d.date() for d in df[col]]
        df[intCols] = df[intCols].astype(int)
        df[numCols] = df[numCols].apply(pd.to_numeric)
        return df

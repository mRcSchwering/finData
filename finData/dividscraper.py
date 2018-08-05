# This Python file uses the following encoding: utf-8
from finData.boersescraper import BoerseScraper
#
# D = DividScraper('Adidas-Aktie', 'DE000A1EWWW0')
# D._table


class DividScraper(BoerseScraper):

    uri = 'dividenden'
    html_search = ['Dividenden']

    # convert scraped names to db col names
    web2db = [
        {'web': 'Datum', 'db': 'datum'},
        {'web': 'Dividende', 'db': 'dividende'},
        {'web': 'Veränderung', 'db': 'veraenderu'},
        {'web': 'Rendite', 'db': 'rendite'}
    ]

    def __init__(self, boerse_name, isin):
        BoerseScraper.__init__(self, boerse_name, isin)
        self._resolve_boerse_url(self.uri)
        self.data = self._getData()

    def _getData(self):
        html_tables = self._getHTMLTables(self.html_search, self._url)
        btable = self._htmlTab2dict(html_tables[html_search], hasRownames=False)
        return btable


    # def getTable(self, text='Dividenden'):
    #     """Scrape dividend table from boerse.de given a h3 text search string"""
    #     req = self._getTables(self.divid_url)
    #     soup = BeautifulSoup(req, 'lxml')
    #     h3 = soup.find(lambda tag: text in tag.text and tag.name == 'h3')
    #     try:
    #         tab = h3.findNext('table')
    #     except AttributeError:
    #         print('Table %s not found' % text)
    #     btab = Scraper._htmlTab2dict(tab, hasRownames=False)
    #     utab = Scraper._decode(btab)
    #     self.divid_table = Scraper._guessTypes(utab)
    #     self.existingTables.append('divid')
    #
    # def get(self, key):
    #     """Return table as pd.DataFrame"""
    #     if key not in Scraper.tables:
    #         raise ValueError('Invalid key, expect one of: %s' % Scraper.tables)
    #     if key not in self.existingTables:
    #         raise ValueError('No data exists for this key' +
    #                          ' existing data: %s' % self.existingTables)
    #     options = {
    #         'divid': lambda: Scraper._toDataFrame(self.divid_table, Scraper.divid_id2name, typ='divid')
    #     }
    #     return options[key]()
    #
    # def _getTables(cls, url):
    #     """Request url for html"""
    #     return requests.get(url).content
    #
    # @classmethod
    # def _guessTypes(cls, obj, defStr=['colnames', 'rownames'],
    #                 defNaN=['n.v.', '', '%', '-', '-%'], rePerc='(^.*)%$',
    #                 reNum='^-?[0-9.]*,[0-9][0-9]*$',
    #                 reDate=[{'re': '^[0-9]{2}.[0-9]{2}.[0-9]{2}$',
    #                          'fmt': '%d.%m.%y'}]):
    #     """Guess and convert types for fundamental tables and dividend table"""
    #     identified = True
    #     if isinstance(obj, dict):
    #         for key in obj:
    #             if key in defStr:
    #                 obj[key] = [str(d) for d in obj[key]]
    #             else:
    #                 obj[key] = cls._guessTypes(obj[key])
    #     elif isinstance(obj, list):
    #         for i in range(len(obj)):
    #             obj[i] = cls._guessTypes(obj[i])
    #     else:
    #         if obj in defNaN:
    #             obj = float('NaN')
    #         elif re.search(rePerc, obj):
    #             x = re.search(rePerc, obj).group(1).replace(',', '.')
    #             x = x.replace(".", "", x.count(".") - 1)
    #             obj = float('NaN') if x in defNaN else float(x) / 100
    #         elif re.search(reNum, obj):
    #             x = obj.replace(',', '.')
    #             x = x.replace(".", "", x.count(".") - 1)
    #             obj = float('NaN') if x in defNaN else float(x)
    #         else:
    #             pass
    #             identified = False
    #             for d in reDate:
    #                 if re.search(d['re'], obj):
    #                     obj = dt.datetime.strptime(obj, d['fmt']).date()
    #                     identified = True
    #                     break
    #         if not identified:
    #             raise ValueError('Value not identified: ' + obj)
    #     return obj
    #
    # @classmethod
    # def _decode(cls, obj):
    #     """
    #     Recursive decoding of objects
    #     """
    #     if isinstance(obj, dict):
    #         for key in obj:
    #             obj[key] = cls._decode(obj[key])
    #     elif isinstance(obj, list):
    #         for i in range(len(obj)):
    #             obj[i] = cls._decode(obj[i])
    #     elif isinstance(obj, bytes):
    #         obj = obj.decode()
    #     return obj
    #
    #
    # @classmethod
    # def _toDataFrame(cls, data, mapping):
    #     """
    #     Convert tables as from _htmlTab2dict into pd.DataFrames as in DB schema
    #     """
    #     tmp = {}
    #     for col in mapping:
    #         if col['web'] in data['colnames']:
    #             idx = data['colnames'].index(col['web'])
    #             tmp[col['db']] = [d[idx] for d in data['data']]
    #         else:
    #             tmp[col['db']] = len(data['data']) * [float('NaN')]
    #     df = pd.DataFrame.from_dict(tmp)
    #     df = df[[c['db'] for c in mapping]]
    #     df['datum'] = pd.to_datetime(df['datum'])
    #     df.sort_values(by='datum', inplace=True)
    #
    #     dateCols = [c for c in df.columns if c in cls.date_columns]
    #     intCols = [c for c in df.columns if c in cls.int_columns]
    #     numCols = [c for c in df.columns if c not in dateCols + intCols]
    #     df[dateCols] = df[dateCols].astype('datetime64[ns]')
    #     for col in dateCols:
    #         df[col] = [d.date() for d in df[col]]
    #     df[intCols] = df[intCols].astype(int)
    #     df[numCols] = df[numCols].apply(pd.to_numeric)
    #     return df

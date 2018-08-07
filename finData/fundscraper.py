# This Python file uses the following encoding: utf-8
from finData.boersescraper import BoerseScraper
from finData.assets.dbColumnConversions import DBColumnConversions
import pandas as pd

# TODO durch fund werte gehen, gucken ob sie sinn machen
# aktien in int? oder lieber pro 1000 in float? oder mio?

# TODO assets lieber als json


class FundScraper(BoerseScraper):

    uri = 'fundamental-analyse'
    html_searches = ['GuV', 'Bilanz', 'Kennzahlen', 'Rentabilität',
                     'Personal', 'Marktkapitalisierung']

    def __init__(self, boerse_name, isin):
        BoerseScraper.__init__(self, boerse_name, isin)
        self.columns = DBColumnConversions.fundamental_yearly
        self._resolve_boerse_url(self.uri)
        self.data = self._getData()

    def _getData(self):
        html_tables = self._getHTMLTables(self.html_searches, self._url)
        tables = {}
        for key in html_tables:
            bytes_table = self._htmlTab2dict(html_tables[key])
            string_table = self._decode(bytes_table)
            tables[key] = self._guessTypes(string_table)
        table = self._concatTables(tables)
        df = self._table2DataFrame(table, self.columns, transpose=True)
        df['zahl_aktien'] = df['zahl_aktien'] * 10**6
        df['jahr'] = df.index.tolist()
        df['jahr'] = df['jahr'].astype(int)
        return df

# This Python file uses the following encoding: utf-8
from finData.boersescraper import BoerseScraper
import pandas as pd


# TODO das ganze für fund


# ADS = ['Adidas-Aktie', 'DE000A1EWWW0']
# divid = DividScraper(*ADS)
# df = divid.data
# df.to_dict(orient='records')
# row = df.loc[[d.year == 1996 for d in df['datum']]]
# row['rendite'].tolist()


class DividScraper(BoerseScraper):

    uri = 'dividenden'
    html_search = 'Dividenden'

    # convert column names from table to DataFrame
    columns = [
        {'from': 'Datum', 'to': 'datum', 'type': 'other'},
        {'from': 'Dividende', 'to': 'dividende', 'type': 'num'},
        {'from': 'Veränderung', 'to': 'veraenderu', 'type': 'num'},
        {'from': 'Rendite', 'to': 'rendite', 'type': 'num'}
    ]

    def __init__(self, boerse_name, isin):
        BoerseScraper.__init__(self, boerse_name, isin)
        self._resolve_boerse_url(self.uri)
        self.data = self._getData()

    def _getData(self):
        html_tables = self._getHTMLTables([self.html_search], self._url)
        bytes_table = self._htmlTab2dict(
            html_tables[self.html_search], hasRownames=False)
        string_table = self._decode(bytes_table)
        table = self._guessTypes(string_table)
        return self._table2DataFrame(table, self.columns)

# This Python file uses the following encoding: utf-8
from finData.boersescraper import BoerseScraper
import pandas as pd


class DividScraper(BoerseScraper):

    uri = 'dividenden'
    html_search = 'Dividenden'
    conversions_filename = 'finData/assets/dbColumnConversions.json'

    def __init__(self, boerse_name, isin):
        BoerseScraper.__init__(self, boerse_name, isin)
        DBColumnConversions = self.getColumnConversions(self.conversions_filename)
        self.columns = DBColumnConversions['dividend_yearly']
        self._resolve_boerse_url(self.uri)
        self.data = self._getData()

    def _getData(self):
        html_tables = self._getHTMLTables([self.html_search], self._url)
        bytes_table = self._htmlTab2dict(
            html_tables[self.html_search], hasRownames=False)
        string_table = self._decode(bytes_table)
        table = self._guessTypes(string_table)
        return self._table2DataFrame(table, self.columns)

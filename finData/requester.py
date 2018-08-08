# This Python file uses the following encoding: utf-8
from finData.dividscraper import DividScraper
from finData.fundscraper import FundScraper

# TODO scraper benutzen
# df = divid.data
# df.to_dict(orient='records')
# row = df.loc[[d.year == 1996 for d in df['datum']]]
# row['rendite'].tolist()

# TODO alphaREST schreiben


class Requester(object):
    """
    Adapter for requesting data using scraper or REST classes.
    """

    def __init__(self, stock):
        self._stock = stock

    def table(self, table, history):
        self._table = table
        self._history = history
        if self._table.name == 'fundamental_yearly':
            return self._getFundData()
        if self._table.name == 'divid_yearly':
            return self._getDividData()
        if self._table.name == 'hist_daily':
            return 'hist'
        raise AttributeError("Requester wasn't able to get table %s" % self._table.name)

    def _getDividData(self):
        obj = DividScraper(self._stock.boerse_name, self._stock.boerse_name)
        return obj.data

    def _getFundData(self):
        obj = FundScraper(self._stock.boerse_name, self._stock.boerse_name)
        return obj.data

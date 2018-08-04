# This Python file uses the following encoding: utf-8


class Requester(object):
    """
    Adapter for requesting data using scraper or REST classes.
    """

    def __init__(self, stock):
        self._stock = stock

    def table(self, table, history):
        self._table = table
        self._history = history
        self.data = self._getData()

    def _getData(self):
        if self._table.name == 'fundamental_yearly':
            return 'fundamental_yearly'
        if self._table.name == 'divid_yearly':
            return 'divid_yearly'
        if self._table.name == 'hist_daily':
            return 'hist_daily'
        raise AttributeError("Requester doesn't know table %s" % self._table.name)

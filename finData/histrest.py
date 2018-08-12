# This Python file uses the following encoding: utf-8
from finData.alphavantageapi import AlphavantagAPI
import pandas as pd


class HistRest(AlphavantagAPI):

    def __init__(self, ticker, days_missing):
        AlphavantagAPI.__init__(self, boerse_name, isin)
        self.data = self._getData(ticker, days_missing)

    def _getData(self, ticker, days_missing):
        """
        Use alphavantage API to request historic prices
        """
        query = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': ticker,
            'outputsize': 'compact' if days_missing <= 100 else 'full'
        }
        df = self._request(query)
        self.data = self._reshape(df)

# This Python file uses the following encoding: utf-8
from finData.alphavantageapi import AlphavantagAPI
import pandas as pd


class HistRest(AlphavantagAPI):

    _conversions_filename = 'finData/assets/dbColumnConversions.json'

    def __init__(self, ticker, days_missing):
        AlphavantagAPI.__init__(self)
        DBColumnConversions = self.getColumnConversions(self._conversions_filename)
        self.columns = DBColumnConversions['hist_daily']
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
        data = self._request(query)
        df = pd.DataFrame \
            .from_dict(data['Time Series (Daily)'], orient='index', dtype=float)
        df_reshaped = self._reshape(df)
        df_reshaped['datum'] = df_reshaped.index
        return df_reshaped

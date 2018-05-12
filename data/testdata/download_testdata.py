# This Python file uses the following encoding: utf-8
import finData.scrape as fDs
import json
import os.path
import pickle

# some stocks for testdata
DAX = [
    {
        'name': 'Adidas',
        'typ': 'Aktie',
        'wkn': 'A1EWWW',
        'isin': 'DE000A1EWWW0',
        'currency': 'EUR',
        'boerse_name': 'Adidas-Aktie',
        'avan_ticker': 'ADS.DE'
    },
    {
        'name': 'Bayer',
        'typ': 'Aktie',
        'wkn': 'BAY001',
        'isin': 'DE000BAY0017',
        'currency': 'EUR',
        'boerse_name': 'Bayer-Aktie',
        'avan_ticker': 'BAYN.DE'
    },
    {
        'name': 'Beiersdorf',
        'typ': 'Aktie',
        'wkn': '520000',
        'isin': 'DE0005200000',
        'currency': 'EUR',
        'boerse_name': 'Beiersdorf-Aktie',
        'avan_ticker': 'BEI.DE'
    },
    {
        'name': 'BMW St',
        'typ': 'Aktie',
        'wkn': '519000',
        'isin': 'DE0005190003',
        'currency': 'EUR',
        'boerse_name': 'BMW-St-Aktie',
        'avan_ticker': 'BMW.DE'
    },
    {
        'name': 'Commerzbank',
        'typ': 'Aktie',
        'wkn': 'CBK100',
        'isin': 'DE000CBK1001',
        'currency': 'EUR',
        'boerse_name': 'Commerzbank-Aktie',
        'avan_ticker': 'CBK.DE'
    },
    {
        'name': 'Deutsche Bank',
        'typ': 'Aktie',
        'wkn': '514000',
        'isin': 'DE0005140008',
        'currency': 'EUR',
        'boerse_name': 'Deutsche-Bank-Aktie',
        'avan_ticker': 'DBK.DE'
    },
    {
        'name': 'Deutsche Börse',
        'typ': 'Aktie',
        'wkn': '581005',
        'isin': 'DE0005810055',
        'currency': 'EUR',
        'boerse_name': 'Deutsche-Boerse-Aktie',
        'avan_ticker': 'DB1.DE'
    }
]

# scrape boerse and request hist prices
data = {}
for i in range(len(DAX)):
    aktie = fDs.Scraper(DAX[i]['name'], DAX[i]['typ'], DAX[i]['wkn'],
                        DAX[i]['isin'], DAX[i]['currency'],
                        DAX[i]['boerse_name'], DAX[i]['avan_ticker'])
    aktie.getDividendTable()
    aktie.getFundamentalTables()
    aktie.getHistoricPrices(onlyLast100=True)
    data[aktie.avan_ticker] = {
        "guv": aktie.get('guv'),
        "bilanz": aktie.get('bilanz'),
        "kennza": aktie.get('kennza'),
        "rentab": aktie.get('rentab'),
        "person": aktie.get('person'),
        "marktk": aktie.get('marktk'),
        "divid": aktie.get('divid'),
        "hist": aktie.get('hist')
    }

# save data as json
basepath = 'data/testdata'
filename = 'testdata.pkl'
with open(os.path.join(basepath, filename), 'wb') as ouf:
    pickle.dump(data, ouf)

# load
# with open(os.path.join(basepath, filename), 'rb') as inf:
#     data2 = pickle.load(inf)

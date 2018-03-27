# This Python file uses the following encoding: utf-8
import finData.scrape as fDs


# python3 -m unittest discover -s test -v

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
        'name': 'Alianz',
        'typ': 'Aktie',
        'wkn': '840400',
        'isin': 'DE0008404005',
        'currency': 'EUR',
        'boerse_name': 'Allianz-Aktie',
        'avan_ticker': 'ALV.DE'
    },
    {
        'name': 'BASF',
        'typ': 'Aktie',
        'wkn': 'BASF11',
        'isin': 'DE000BASF111',
        'currency': 'EUR',
        'boerse_name': 'BASF-Aktie',
        'avan_ticker': 'BAS.DE'
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
        'name': 'Continental',
        'typ': 'Aktie',
        'wkn': '543900',
        'isin': 'DE0005439004',
        'currency': 'EUR',
        'boerse_name': 'Continental-Aktie',
        'avan_ticker': 'CON.DE'
    },
    {
        'name': 'Daimler',
        'typ': 'Aktie',
        'wkn': '710000',
        'isin': 'DE0007100000',
        'currency': 'EUR',
        'boerse_name': 'Daimler-Aktie',
        'avan_ticker': 'DAI.DE'
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


len(DAX)
i = 7
aktie = fDs.Scraper(DAX[i]['name'], DAX[i]['typ'], DAX[i]['wkn'], DAX[i]['isin'],
                    DAX[i]['currency'], DAX[i]['boerse_name'], DAX[i]['avan_ticker'])


aktie.getDividendTable()
aktie.getFundamentalTables()

aktie.get('guv')
aktie.get('bilanz')
aktie.get('marktk')
aktie.get('kennza')
aktie.get('rentab')

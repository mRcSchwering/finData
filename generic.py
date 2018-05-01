# This Python file uses the following encoding: utf-8
import finData.scrape as fDs


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

data = []
for i in range(len(DAX)):
    aktie = fDs.Scraper(DAX[i]['name'], DAX[i]['typ'], DAX[i]['wkn'],
                        DAX[i]['isin'], DAX[i]['currency'],
                        DAX[i]['boerse_name'], DAX[i]['avan_ticker'])
    aktie.getDividendTable()
    aktie.getFundamentalTables()
    aktie.getHistoricPrices()
    data.append({
        "guv": aktie.get('guv'),
        "bilanz": aktie.get('bilanz'),
        "kennza": aktie.get('kennza'),
        "rentab": aktie.get('rentab'),
        "person": aktie.get('person'),
        "marktk": aktie.get('marktk'),
        "divid": aktie.get('divid'),
        "hist": aktie.get('hist')
    })
d = data[2]
type(d.get("hist"))
d.get("hist").get("data")

# TODO: multiple insert (https://stackoverflow.com/questions/8134602/psycopg2-insert-multiple-rows-with-one-query)
# TODO: Daten convertieren und in DB schreiben
# TODO: Daten irgendwie abspeichern (fürs repo)

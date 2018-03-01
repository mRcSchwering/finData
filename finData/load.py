"""Short Description.

Detailed Description
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

#import pandas_datareader as pdr   # deprecated prd.get_data_yahoo ???
#import pandas_datareader.data as web # usable DataReader ???
#from tiingo import TiingoClient # useful??: No!

import datetime
import urllib2
from bs4 import BeautifulSoup



def htmlTab2dict(tab,
                 hasRownames = True,
                 hasColnames = True,
                 removeEmpty = True,
                 checkTable = True):
    """Return dict of lists from html table string"""
    rows = tab.findAll('tr')
    rownamesIdx = 0 if hasRownames else -1
    colnamesIdx = 0 if hasColnames else -1

    data = []
    nonEmptyRowIdxs = []
    for idx, row in enumerate(rows[(colnamesIdx+1):]):
        thisRow = []
        for col in row.findAll('td')[(rownamesIdx+1):]:
            text = col.text.replace(u'\xa0', u' ').encode('utf-8').strip()
            thisRow.append(text)
        if not removeEmpty or not all(d == '' for d in thisRow):
            data.append(thisRow)
            nonEmptyRowIdxs.append(idx + (colnamesIdx+1))
    out = {'data': data}

    if hasRownames:
        rownames = []
        for row in [rows[i] for i in nonEmptyRowIdxs]:
            text = row.find('td').text.replace(u'\xa0', u' ').encode('utf-8').strip()
            rownames.append(text)
        out['rownames'] = rownames

    if hasColnames:
        colnames = []
        tag = 'th' if len(rows[colnamesIdx].findAll('th')) > 0 else 'td'
        for col in rows[colnamesIdx].findAll(tag)[(rownamesIdx+1):]:
            text = col.text.replace(u'\xa0', u' ').encode('utf-8').strip()
            colnames.append(text)
        out['colnames'] = colnames

    if checkTable and len(out['data']) > 1:
        lens = [len(row) for row in out['data']]
        diffs = map(lambda x: x[0] - x[1], zip(lens, lens[1:] + [lens[0]]))
        if not all(d == 0 for d in diffs):
            raise UserWarning('Data rows do not all have the same lengths')

    return out




def FundamentalTables(url_chr,
                      ids = ['guv', 'bilanz', 'kennzahlen', 'rentabilitaet', 'personal'],
                      texts = ['Marktkapitalisierung']):
    """Scrape fundamental data tables from boerse.de given h3 Ids or h3 text search strings"""
    tabDict = {}
    soup = BeautifulSoup(urllib2.urlopen(url_chr), 'lxml')
    for id in ids:
        h3 = soup.find(lambda tag: tag.get('id') == id and tag.name == 'h3')
        try:
            tabDict[id.lower()[:6]] = h3.findNext('table')
        except AttributeError:
            print('Table %s was not found' % id)
    for text in texts:
        h3 = soup.find(lambda tag: text in tag.text and tag.name == 'h3')
        try:
            tabDict[text.lower()[:6]] = h3.findNext('table')
        except AttributeError:
            print('Table %s was not found' % text)

    out = {}
    for key, tab in tabDict.iteritems():
        out[key] = htmlTab2dict(tab, hasRownames=True, hasColnames=True, removeEmpty=True)
    return out




def DividendTable(url_chr, text = 'Dividenden'):
    soup = BeautifulSoup(urllib2.urlopen(url_chr), 'lxml')
    h3 = soup.find(lambda tag: text in tag.text and tag.name == 'h3')
    try:
        tab = h3.findNext('table')
    except AttributeError:
        print('Table %s not found' % text)
    return htmlTab2dict(tab, hasRownames=False)





# TODO eigene API bauen!!

ticker = "ADS"
start = datetime.datetime(1990, 1, 1)

def HistoricPrices(ticker,
                   start = datetime.datetime(1990, 1, 1)):
    """Download historic prices from yahoo! using ticker symbol"""
    # koennte man auch scrapen (aber dann ohne adjusted Prices)
    # Bsp: https://www.boerse.de/historische-kurse/BB-Biotech-Aktie/CH0038389992_seite,231,anzahl,20
    #return pdr.get_data_yahoo(ticker, start=start)
    #return web.DataReader(ticker, "yahoo", start=start)

# testStock = [
#     {
#         'Name': 'Addidas AG',
#         'Typ': 'Aktie',
#         'WKN': 'A1EWWW',
#         'ISIN': 'DE000A1EWWW0',
#         'yahooTicker': 'ADS.DE',
#         'boerseURL': 'Adidas-Aktie/DE000A1EWWW0'
#     },
#     {
#         'Name': 'BB Biotech',
#         'Typ': 'Aktie',
#         'WKN': 'A0NFN3',
#         'ISIN': 'CH0038389992',
#         'yahooTicker': 'BBZA.DE',
#         'boerseURL': 'BB-Biotech-Aktie/CH0038389992'
#     }
# ]
# boerseDe = {
#     'host': 'www.boerse.de',
#     'pathFund': 'fundamental-analyse',
#     'pathDivid': 'dividenden'
# }
#
# Fund_url = 'https://%s/%s/%s' % (boerseDe['host'], boerseDe['pathFund'], testStock[1]['boerseURL'])
# Divid_url = 'https://%s/%s/%s' % (boerseDe['host'], boerseDe['pathDivid'], testStock[1]['boerseURL'])



def main():
    pass

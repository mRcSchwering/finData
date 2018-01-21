"""Short Description.

Detailed Description
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pandas_datareader as pdr
import datetime
import urllib2
from bs4 import BeautifulSoup



def getHistoricPrices(tickers_arr,
                      prefix="",
                      suffix="",
                      start=datetime.datetime(1990, 1, 1),
                      verbose=False):
    """Download financial data from yahoo! using ticker symbol"""
    data = {}
    for tick in tickers_arr:
        symbol = prefix + tick + suffix
        if verbose:
            print("\nDownloading %s from yahoo!..." % symbol)
        try:
            data[tick] = pdr.get_data_yahoo(symbol, start=start)
        except:
            print("%s could not be downloaded!" % symbol)
    return data


def extractText(contents):
    """Extract text from soup contents arr recursively"""
    text = []
    for cont in contents:
        try:
            newConts = cont.contents
            text.append(extractText(newConts))
        except AttributeError:
            text.append(cont.string)
    return "".join(text)


def scrapeWikiTable(url_chr, class_chr="wikitable sortable"):
    """Used for getting info about indices like DAX or so"""
    soup = BeautifulSoup(urllib2.urlopen(url_chr), "lxml")
    table = soup.find("table", class_=class_chr)
    tabRows = table.find_all("tr")

    header = []
    for cell in tabRows[0].find_all("th"):
        header.append(extractText(cell.contents))

    body = []
    for row in tabRows[1:]:
        rowText = []
        for cell in row.find_all("td"):
            rowText.append(extractText(cell.contents))
        body.append(rowText)

    return {"head": header, "body": body}




# testStock = {
#     'Name': 'Addidas AG',
#     'Typ': 'Aktie',
#     'WKN': 'A1EWWW',
#     'ISIN': 'DE000A1EWWW0',
#     'yahooTicker': 'ADS.DE',
#     'boerseURL': 'Adidas-Aktie/DE000A1EWWW0'
# }
# boerseDe = {
#     'host': 'www.boerse.de',
#     'pathFund': 'fundamental-analyse',
#     'pathDivid': 'dividenden'
# }
#
# url_chr = 'https://%s/%s/%s' % (boerseDe['host'], boerseDe['pathDivid'], testStock['boerseURL'])




def htmlTab2dict(tab, hasRownames=True, hasColnames=True, removeEmpty=True):
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

    if len(out['data']) > 1:
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
    soup = BeautifulSoup(urllib2.urlopen(url_chr), "lxml")
    for id in ids:
        h3 = soup.find(lambda tag: tag.get('id') == id and tag.name == 'h3')
        tabDict[id.lower()[:6]] = h3.findNext('table')
    for text in texts:
        h3 = soup.find(lambda tag: text in tag.text and tag.name == 'h3')
        tabDict[text.lower()[:6]] = h3.findNext('table')

    out = {}
    for key, tab in tabDict.iteritems():
        out[key] = htmlTab2dict(tab, hasRownames=True, hasColnames=True, removeEmpty=True)
    return out




def DividendTable(url_chr, text='Dividenden'):
    soup = BeautifulSoup(urllib2.urlopen(url_chr))
    h3 = soup.find(lambda tag: text in tag.text and tag.name == 'h3')
    tab = h3.findNext('table')
    return htmlTab2dict(tab, hasRownames=False)





def main():
    pass

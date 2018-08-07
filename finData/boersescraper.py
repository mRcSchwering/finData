# This Python file uses the following encoding: utf-8
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
import requests
import re


class BoerseScraper(object):
    """
    Scrape dividend table from boerse.de
    """

    host = 'www.boerse.de'

    def __init__(self, boerse_name, isin):
        self._isin = isin
        self._boerse_name = boerse_name

    def _resolve_boerse_url(self, uri):
        pre = 'https://' + self.host
        post = self._boerse_name + '/' + self._isin
        self._url = '/'.join([pre, uri, post])

    def _getHTMLTables(self, search_texts, url, header=['h2', 'h3']):
        """
        Scrape tables from boerse.de given a list of h3 text search strings
        """
        req = self._requestURL(url)
        soup = BeautifulSoup(req, 'lxml')
        tableDict = {}
        for text in search_texts:
                h = soup.find(lambda tag: text in tag.text and tag.name in header)
                try:
                    table = h.findNext('table')
                except AttributeError:
                    raise AttributeError('Table %s not found' % text)
                tableDict[text] = table
        return tableDict

    @classmethod
    def _requestURL(cls, url):
        return requests.get(url).content

    @classmethod
    def _htmlTab2dict(cls, html_table, hasRownames=True, hasColnames=True,
                      removeEmptyRows=True, validateTable=True):
        """
        Return dictionary given html table as tag

        Dict with lists for rownames and colnames if applicable
        and data as list of rows which have lists of column values
        """
        rows = html_table.findAll('tr')
        rownamesIdx = 0 if hasRownames else -1
        colnamesIdx = 0 if hasColnames else -1

        data = []
        nonEmptyRowIdxs = []
        for idx, row in enumerate(rows[(colnamesIdx+1):]):
            thisRow = []
            for col in row.findAll('td')[(rownamesIdx+1):]:
                text = col.text.replace(u'\xa0', u' ').encode('utf-8').strip()
                thisRow.append(text)
            if not removeEmptyRows or not all(d in [u'', b''] for d in thisRow):
                data.append(thisRow)
                nonEmptyRowIdxs.append(idx + (colnamesIdx+1))
        out = {'data': data}

        if hasRownames:
            rownames = []
            for row in [rows[i] for i in nonEmptyRowIdxs]:
                text = row.find('td') \
                    .text.replace(u'\xa0', u' ') \
                    .encode('utf-8').strip()
                rownames.append(text)
            out['rownames'] = rownames

        if hasColnames:
            colnames = []
            tag = 'th' if len(rows[colnamesIdx].findAll('th')) > 0 else 'td'
            for col in rows[colnamesIdx].findAll(tag)[(rownamesIdx+1):]:
                text = col.text.replace(u'\xa0', u' ').encode('utf-8').strip()
                colnames.append(text)
            out['colnames'] = colnames

        if validateTable and len(out['data']) > 1:
            lens = [len(row) for row in out['data']]
            diffs = map(lambda x: x[0] - x[1], zip(lens, lens[1:] + [lens[0]]))
            if not all(d == 0 for d in diffs):
                raise AttributeError('Data rows do not all have the same lengths')
        return out

    @classmethod
    def _decode(cls, obj):
        """
        Recursive decoding of objects
        """
        if isinstance(obj, dict):
            for key in obj:
                obj[key] = cls._decode(obj[key])
        elif isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = cls._decode(obj[i])
        elif isinstance(obj, bytes):
            obj = obj.decode()
        return obj

    @classmethod
    def _guessTypes(cls, obj,
                    str_list_keys=['colnames', 'rownames'],
                    NaN_strs=['n.v.', '', '%', '-', '-%'],
                    perc_regexs=['(^.*)%$'],
                    num_regexs=['^-?[0-9.]*,[0-9][0-9]*$'],
                    int_regexs=['^-?[0-9]*$', '^-?[0-9]*(\.[0-9]{3})+$'],
                    dates=[{
                            'regex': '^[0-9]{2}.[0-9]{2}.[0-9]{2}$',
                            'format': '%d.%m.%y'
                        }, {
                            'regex': '^[0-9]{2}.[0-9]{2}.[0-9]{4}$',
                            'format': '%d.%m.%Y'
                        }]):
        """
        Recursively guess and convert types in obj of dicts and lists
        """
        def guessValue(obj):
            if obj in NaN_strs:
                return float('NaN')
            for regex in perc_regexs:
                if re.search(regex, obj):
                    x = re.search(regex, obj) \
                        .group(1) \
                        .replace(".", "") \
                        .replace(',', '.')
                    return float('NaN') if x in NaN_strs else float(x) / 100
            for date in dates:
                if re.search(date['regex'], obj):
                    return dt.datetime \
                        .strptime(obj, date['format']) \
                        .date()
            for regex in num_regexs:
                if re.search(regex, obj):
                    x = obj.replace(".", "").replace(',', '.')
                    return float('NaN') if x in NaN_strs else float(x)
            for regex in int_regexs:
                if re.search(regex, obj):
                    x = obj.replace(".", "")
                    return float('NaN') if x in NaN_strs else int(x)
            raise ValueError('Value not identified: %s' % obj)

        if isinstance(obj, dict):
            for key in obj:
                if key in str_list_keys:
                    obj[key] = [str(d) for d in obj[key]]
                else:
                    obj[key] = cls._guessTypes(obj[key])
        elif isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = cls._guessTypes(obj[i])
        else:
            obj = guessValue(obj)

        return obj

    @classmethod
    def _concatTables(cls, tables):
        keys = list(tables.keys())
        k = 1
        for i in range(len(tables) - 1):
            if not tables[keys[i]]['colnames'] == tables[keys[k]]['colnames']:
                raise AttributeError('Tables have differing columns')
            k += 1
        for key in tables:
            if len(tables[key]['rownames']) != len(tables[key]['data']):
                raise AttributeError('Rownames length and number of rows differs')
        rownames = []
        rows = []
        for key in keys:
            rownames = rownames + tables[key]['rownames']
            rows = rows + tables[key]['data']
        if len(rownames) != len(set(rownames)):
            raise AttributeError('Tables have duplicate rownames')
        table = {
            'colnames': tables[keys[0]]['colnames'],
            'rownames': rownames,
            'data': rows
        }
        return table

    @classmethod
    def _table2DataFrame(cls, table, mapping, transpose=False):
        """
        Convert table into DataFrame using a mapping

        Mapping is list of dicts with each 'from' and 'to'.
        DataFrame columns are renamed 'from', 'to'.

        Names not appearing in mapping are not included in dataframe.

        Optional transposition happens before mapping.
        """
        rownames = table.get('rownames')
        colnames = table.get('colnames')
        data = table.get('data')
        df = pd.DataFrame(data, index=rownames, columns=colnames)
        if transpose:
            df = df.T
        old_colnames = [c['from'] for c in mapping]
        df = df[old_colnames]
        new_colnames = []
        for old in old_colnames:
            new = [c['to'] for c in mapping if c['from'] == old]
            new_colnames.append(new[0])
        df.columns = new_colnames
        return df

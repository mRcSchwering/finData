# This Python file uses the following encoding: utf-8
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
import os
import re
import json
import requests

# TODO _htmlTab2dict testen


class BoerseScraper(object):
    """
    Scrape dividend table from boerse.de
    """

    host = 'www.boerse.de'

    # column type conversions
    date_columns = ['datum']
    int_columns = ['year']

    def __init__(self, boerse_name, isin):
        self._isin = isin
        self._boerse_name = boerse_name

    def _resolve_boerse_url(self, uri):
        pre = 'https://' + self.host
        post = self._boerse_name + '/' + self._isin
        self._url = '/'.join([pre, uri, post])

    def _getHTMLTables(self, search_texts, url):
        """
        Scrape tables from boerse.de given a list of h3 text search strings
        """
        req = self._requestURL(url)
        soup = BeautifulSoup(req, 'lxml')
        tableDict = {}
        for text in search_texts:
                h3 = soup.find(lambda tag: text in tag.text and tag.name == 'h3')
                try:
                    table = h3.findNext('table')
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

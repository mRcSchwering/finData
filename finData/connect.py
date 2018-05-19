# This Python file uses the following encoding: utf-8
from psycopg2.extensions import AsIs
import psycopg2 as pg

#x = Connector('findata', 'testdb', 'postgres', '127.0.0.1', 5432)


class Connector(object):
    """DB Connector for SELECTing and INSERTing data"""

    tables = ['guv', 'bilanz', 'kennza', 'rentab', 'person', 'marktk', 'divid', 'hist']

    # definitions of primary table in DB (columns without id)
    unique_const = 'isin'
    prim_cols = ("'{name}','{isin}','{wkn}','{typ}','{currency}',"
                 "'{boerse_name}','{avan_ticker}'")

    # column definition of secondary tables in DB (without id, stock_id)
    sec_cols = {
        'guv': "{year},{umsatz},{bruttoergeb},{EBIT},{EBT},{jahresueber},{dividendena}",
        'bilanz': ("{year},{umlaufvermo},{anlagevermo},{sum_aktiva},{kurzfr_verb},"
                   "{langfr_verb},{gesamt_verb},{eigenkapita},{sum_passiva},"
                   "{eigen_quote},{fremd_quote}"),
        'kennza': ("{year},{gewinn_verw},{gewinn_unvw},{umsatz},{buchwert},"
                   "{dividende},{KGV},{KBV},{KUV}"),
        'rentab': "{year},{umsatzren},{eigenkapren},{geskapren},{dividren}",
        'marktk': "{year},{zahl_aktien},{marktkapita}",
        'divid': "'{datum}',{dividende},{veraenderu},{rendite}",
        'hist': ("'{datum}',{open},{high},{low},{close},"
                 "{adj_close},{volume},{divid_amt},{split_coef}")
    }

    def __init__(self, db_name, schema_name, user, host, port, password=""):
        self.schema_name = str(schema_name)
        self.db_name = str(db_name)
        self.user = str(user)
        self.host = str(host)
        self.port = int(port)
        self.password = str(password)
        self.conn = self._connect()

    def _connect(self):
        """Return mere DB connection"""
        if self.password == "":
            return pg.connect(dbname=self.db_name, user=self.user,
                              host=self.host, port=self.port)
        else:
            return pg.connect(dbname=self.db_name, user=self.user,
                              host=self.host, port=self.port, password=self.password)

    @classmethod
    def _insertNewStockRow(cls, row, schema, conn):
        """INSERT dict of new stock into stock table, return the assigned id"""
        cols = cls.prim_cols \
            .replace("'", "").replace('"', '') \
            .replace("{", "").replace("}", "")
        vals = [cls.prim_cols.format(**row)]
        with conn.cursor() as cur:
            cur.execute(cls._insertStatement(schema, 'stock', cols, vals))
            cur.execute(
                """SELECT id FROM {sc}.stock WHERE {unq} = '{isin}'"""
                .format(sc=schema, unq=AsIs(cls.unique_const), isin=row['isin'])
            )
            stockId = cur.fetchone()
        return stockId[0]

    @classmethod
    def _insertStatement(cls, schema, table, cols, vals):
        """Statement string from column name str and value rows as list of str"""
        return """INSERT INTO {schema}.{table} ({cols}) VALUES {vals}""" \
               .format(schema=AsIs(schema), table=AsIs(table),
                       cols=cols, vals='({})'.format('),('.join(vals)))

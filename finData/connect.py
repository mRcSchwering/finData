# This Python file uses the following encoding: utf-8
"""Short Description.

Detailed Description
"""

from psycopg2.extensions import AsIs
import psycopg2


class Connector(object):

    tables = ['guv', 'bilanz', 'kennza', 'rentab', 'person', 'marktk', 'divid', 'hist']

    def __init__(self, schema_name, db_name, user, host, port, password="", table=None):
        self.schema_name = str(schema_name)
        self.db_name = str(db_name)
        self.user = str(user)
        self.host = str(host)
        self.port = int(port)
        self.password = str(password)
        self.conn = self._connect()
        if table is not None:
            self.table = setTable(table)
        else:
            self.table = table

    def setTable(self, table):
        if table not in Connector.tables:
            raise ValueError('Invalid table, expect one of: %s' % Connector.tables)
        self.table = table

    def _connect(self):
        if password == "":
            return psycopg2.connect(dbname=self.db_name, user=self.user,
                                    host=self.host, port=self.port)
        else:
            return psycopg2.connect(dbname=self.db_name, user=self.user,
                                    host=self.host, port=self.port, password=self.password)

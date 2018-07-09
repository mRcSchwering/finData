# This Python file uses the following encoding: utf-8
import psycopg2 as pg


class DBConnector(object):
    """
    Connection to database
    """

    def __init__(self, db, user, host, port, password=""):
        self.name = str(db)
        self.user = str(user)
        self.host = str(host)
        self.port = int(port)
        self.password = str(password)
        self.conn = self._connect()

    def query(self, statement, arguments, fetch=None):
        """
        Execute custom query as is and fetch 'one'/'all' if needed
        """
        res = None
        with self.conn as con:
            with con.cursor() as cur:
                cur.execute(statement, arguments)
                if fetch == 'all':
                    res = cur.fetchall()
                if fetch == 'one':
                    res = cur.fetchone()
        return res

    def _connect(self):
        """
        Return mere DB connection
        """
        if self.password == "":
            return pg.connect(dbname=self.name, user=self.user,
                              host=self.host, port=self.port)
        else:
            return pg.connect(dbname=self.name, user=self.user,
                              host=self.host, port=self.port, password=self.password)

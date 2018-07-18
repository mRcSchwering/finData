# This Python file uses the following encoding: utf-8
from finData.connect import Connector
import argparse

# TODO testdata updaten
# stock der nciht existet (also einen vorhalten)
# stock mit daten, die aktuell sind
# stock mit daten die alt sind
# stock ohne daten

# TODO TODOs in timeline.py

# TODO Klasse 'Request' als adapter für 'BoerseScraper' und 'AlphaREST'
# mit 'table()' für Tabellen Namen wird entsprechende Methode benutzt in
# 'Boerse*' oder 'Alpha*' um Daten zu kriegen requesten/scrapen

# TODO 'AlphaREST' Klasse implementieren
# TODO 'REST' Basisklasse implementieren

# TODO 'BoerseScraper' Klasse implementieren
# TODO 'Scraper' Basisklasse implementieren

# TODO FindataFacade und main mit Klassen implementieren
# TODO integration tests damit
# TODO alten code löschen

# TODO csv reader adden für insert stock
# TODO add currency constraints via SQL
# TODO logger anstatt print


class FindataFacade(object):
    """
    Providing interface to main module functions
    """

    # update limit in years (going into the past from today)
    update_limit = 20

    def __init__(self, db_name, user, host, port,
                 password, schema_name, stock_table):
        self._db = DBConnector(db_name, user, host, port, password)
        self._schema = Schema(schema_name, stock_table, self._db)
        self._stock = Stock(self._db, self._schema)

    def insertStock(self, name, isin, currency, boerse_name, avan_ticker):
        """
        Insert stock symbol into stocks table if it doesnt already exist
        """
        res = self._stock.insert(name, isin, currency, avan_ticker, boerse_name)
        return res

    def updateData(self):
        """
        Bring data for each stock symbol in database up to todays date
        """
        isins = self._getAllStockISINs()
        n = len(isins)
        for isin in range(n):
            self._stock.exists(isin)
            print("\n[{i}/{n}]\tUpdating {name} ({isin})..."
                  .format(i=i+1, n=n, name=self._stock.name, isin=self._stock.isin))
            self.updateSingleStock()
        print("...done")
        return True

    def updateSingleStock(self):
        """
        Bring data for a single stock symbol up to todays date
        """
        date_today = self._getDateToday()
        self._request(self._stock, self.update_limit)
        table_names = ['divid_yearly', 'fundamental_yearly', 'hist_daily']
        for table_name in table_names:
            table = self._schema.table(table_name)
            update_rate = table.update_rate
            latest_update = table.latestUpdate()
            self._request.table(table, update_rate, latest_update, date_today)


if __name__ == "__main__":

    # TODO die hier würden mit FindataFacade laufen

    parser = argparse.ArgumentParser(
        description='INSERTing and SELECTing methods',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()

    def fun_insert(args):
        connector = Connector(args.db_name, args.db_schema, args.user,
                              args.host, args.port, args.password)
        connector.insertStock(args.name, args.ISIN, args.WKN, args.type,
                              args.currency, args.boerse_name, args.avan_ticker)

    def fun_update(args):
        print('updating')
        connector = Connector(args.db_name, args.db_schema, args.user,
                              args.host, args.port, args.password)
        connector.updateData()

    # main parser for connection
    parser.add_argument(
        '--schema', dest='db_schema', type=str, help='schema name',
        required=True)
    parser.add_argument(
        '--db', dest='db_name', type=str, help='database name',
        default='findata')
    parser.add_argument(
        '--user', dest='user', type=str, help='user name', default='postgres')
    parser.add_argument(
        '--pass', dest='password', type=str, default='',
        help='user password if any')
    parser.add_argument(
        '--port', dest='port', type=int, help='port', default=5432)
    parser.add_argument(
        '--host', dest='host', type=str, help='host', default='server')

    # insert stock subparser
    parser_insert = subparsers.add_parser(
        'insert', help='Insert new stock symbol into database')
    parser_insert.add_argument('name', type=str, help='stock name')
    parser_insert.add_argument('ISIN', type=str, help='ISIN of stock')
    parser_insert.add_argument('WKN', type=str, help='WKN of stock')
    parser_insert.add_argument(
        'currency', type=str, choices=currencies, help='traded currency')
    parser_insert.add_argument(
        'boerse_name', type=str,
        help='Name used by boerse.de to request data for this stock')
    parser_insert.add_argument(
        'avan_ticker', type=str, help='Ticker as used by alphavantage API')
    parser_insert.add_argument(
        '--type', dest='type', type=str, help='Currently unused',
        default='Aktie')
    parser_insert.set_defaults(func=fun_insert)

    # TODO insert_csv parser

    # update data subparser
    parser_update = subparsers.add_parser(
        'update', help='Update all tables for each stock in database')
    parser_update.set_defaults(func=fun_update)

    # run commands
    args = parser.parse_args()
    args.func(args)

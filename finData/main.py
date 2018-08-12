# This Python file uses the following encoding: utf-8
from finData.dbconnector import DBConnector
from finData.schema import Schema
from finData.stock import Stock
from finData.history import History
import argparse

# TODO None Fehler analysieren
# manchmal ist in integration test history.last_update None... kA wieso

# TODO Klasse 'Request' todos

# TODO 'AlphaREST' Klasse implementieren
# TODO 'REST' Basisklasse implementieren

# TODO integration tests damit
# TODO alten code löschen

# TODO csv reader adden für insert stock
# TODO add currency constraints via SQL
# TODO logger anstatt print


# facade = FindataFacade('findata_test', 'postgres', 'localhost', 5432, '',
#                        'findata_init2', 'stock')
# facade.updateData()


class FindataFacade(object):
    """
    Providing interface to main module functions
    """

    def __init__(self, db_name, user, host, port,
                 password, schema_name, stock_table):
        self._db = DBConnector(db_name, user, host, port, password)
        self._schema = Schema(schema_name, stock_table, self._db)
        self._stock = Stock(self._db, self._schema)
        self._history = None

    def insertStock(self, name, isin, currency, boerse_name, avan_ticker):
        """
        Insert stock symbol into stocks table if it doesnt already exist
        """
        return self._stock.insert(name, isin, currency, avan_ticker, boerse_name)

    def updateData(self):
        """
        Bring data for each stock symbol in database up to todays date
        """
        isins = self._schema.getISINs()
        if isins is None or len(isins) < 1:
            print('No stock symbol in database ...done')
            return True
        n = len(isins)
        for i in range(n):
            self._stock.exists(isins[i])
            print("\n[{i}/{n}]\tUpdating {name} ({isin})..."
                  .format(i=i+1, n=n, name=self._stock.name, isin=self._stock.isin))
            self.updateSingleStock()
        print("...done")
        return True

    def updateSingleStock(self):
        """
        Bring data for a single stock symbol up to todays date
        """
        print('\tin updateSingleStock')
        self._history = History(self._schema, self._stock._id)
        for table in [tab for tab in self._schema.tables if tab != self._schema.stock_table]:
            print('table: %s' % table)
            self._history.table(table)
            rate = self._history.update_rate
            print('\tUpdate rate is: %s' % rate)
            print('\tLast update was: %s' % self._history.last_update)
            if rate == 'daily':
                print('\t%s days missing' % self._history.days_missing)
            else:
                print('\t%s years missing' % self._history.years_missing)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Program for finData database',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()

    def fun_insert(args):
        print('fun_insert called')
        return None

    def fun_update(args):
        print('fun_update called')
        return None

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
    parser_insert.add_argument(
        'currency', type=str, help='traded currency (EUR, USD,...)')
    parser_insert.add_argument(
        'boerse_name', type=str,
        help='Name used by boerse.de to request data for this stock')
    parser_insert.add_argument(
        'avan_ticker', type=str, help='Ticker as used by alphavantage API')
    parser_insert.set_defaults(func=fun_insert)

    # TODO insert_csv parser

    # update data subparser
    parser_update = subparsers.add_parser(
        'update', help='Update all tables for each stock in database')
    parser_update.set_defaults(func=fun_update)

    # run commands
    args = parser.parse_args()
    args.func(args)

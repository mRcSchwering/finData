# This Python file uses the following encoding: utf-8
from finData.connect import Connector
import argparse

# TODO Schema Klasse, die schema Logik und constraints bereit stellt
# TODO Facade für main module function programmieren
# TODO Connector sollte nur DB connection bereit stellen (high lvl logik in Facade)
# TODO Scraper sollte nicht in Connector sein
# TODO unterhalb von Facade nur explizit Dependency Injection


class FindataFacade(object):
    """
    Providing interface to main module functions
    """

    # update limit in years (going into the past from today)
    update_limit = 20

    # tables with yearly or daily indices (and updates)
    # or with a date index which represents the whole year
    year_tables = ['guv', 'bilanz', 'kennza', 'rentab', 'person', 'marktk']
    day_tables = ['hist']
    date_tables = ['divid']

    # column definitions as in DB schema
    col_def = {
        'guv': ['stock_id', 'year', 'umsatz', 'bruttoergeb', 'EBIT', 'EBT', 'jahresueber', 'dividendena'],
        'bilanz': ['stock_id', 'year', 'umlaufvermo', 'anlagevermo', 'sum_aktiva', 'kurzfr_verb', 'langfr_verb', 'gesamt_verb', 'eigenkapita', 'sum_passiva', 'eigen_quote', 'fremd_quote'],
        'kennza': ['stock_id', 'year', 'gewinn_verw', 'gewinn_unvw', 'umsatz', 'buchwert', 'dividende', 'KGV', 'KBV', 'KUV'],
        'rentab': ['stock_id', 'year', 'umsatzren', 'eigenkapren', 'geskapren', 'dividren'],
        'person': ['stock_id', 'year', 'personal', 'aufwand', 'umsatz', 'gewinn'],
        'marktk': ['stock_id', 'year', 'zahl_aktien', 'marktkapita'],
        'divid': ['stock_id', 'datum', 'dividende', 'veraenderu', 'rendite'],
        'hist': ['stock_id', 'datum', 'open', 'high', 'low', 'close', 'adj_close', 'volume', 'divid_amt', 'split_coef']
    }

    def __init__(self, connector, scraper):
        self._connector = connector
        self._scraper = scraper


if __name__ == "__main__":
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

    # update data subparser
    parser_update = subparsers.add_parser(
        'update', help='Update all tables for each stock in database')
    parser_update.set_defaults(func=fun_update)

    # run commands
    args = parser.parse_args()
    args.func(args)

# This Python file uses the following encoding: utf-8
from finData.connect import Connector
import argparse


# TODO mal main methode "halb" schreiben
# wie würde update prozedur verlaufen mit db, schema, stock

# TODO sowas wie 'Update' Klasse um über 'update_limit', 'date_today', und zusammen
# mit 'Table.latestUpdate()' und 'Table.update_rate' berechnen wie lange letztes
# update in table her war -> braucht schema
# braucht stock_id oder stock mit isin

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

    def __init__(self):
        # DBConnector()
        # Schema()
        # Update()
        pass

    def insertStock(self, name, isin, wkn, typ, currency, boerse_name, avan_ticker):
        """
        Insert stock symbol into stocks table if it doesnt already exist
        """
        res = self._conn.stockIdFromISIN(isin)
        if res is not None and len(res) > 0:
            print('{name} (isin: {isin}) not inserted, it already exists'
                  .format(name=name, isin=isin))
        else:
            self._conn.insertStock(
                name, isin, wkn, typ, currency, boerse_name, avan_ticker)
            print('{name} (isin: {isin}) inserted'.format(name=name, isin=isin))

    def updateData(self):
        """
        Bring data for each stock symbol in database up to todays date
        """
        # with self.conn as con:
        #     with con.cursor() as cur:
        #         cur.execute("""SELECT id, name, isin FROM %(schema)s.stock""",
        #                     {'schema': AsIs(self.schema_name)})
        #         stockIds = cur.fetchall()
        # TODO aus auskommentierten oben, methoden unten machen
        stocks = self._conn.getAllStockSymbols()
        n = len(stocks)
        for i in range(n):
            stock = stocks[i]
            print("\n[{i}/{n}]\tUpdating {name} ({isin})..."
                  .format(i=i+1, n=n, name=stock[i][1], isin=stocks[i][2]))
            self.updateSingleStock(stocks[i][0])
        print("...done")
        return True

    def updateSingleStock(self, stockId):
        """
        Bring data for a single stock symbol up to todays date
        """
        # with self.conn as con:
        #     with con.cursor() as cur:
        #         cur.execute("""SELECT * FROM %(schema)s.stock WHERE id = %(id)s""",
        #                     {'schema': AsIs(self.schema_name), 'id': stockId})
        #         res = cur.fetchone()[1:]
        # TODO vllt kann man die (oben) mit getAllStockSymbols() methode
        # kombinieren (muss noch implementiert werden)
        res = self._conn.getStockSymbol()
        stockInfo = {
            'name': res[0],
            'isin': res[1],
            'wkn': res[2],
            'typ': res[3],
            'currency': res[4],
            'boerse_name': res[5],
            'avan_ticker': res[6]
        }
        stock = fDs.Scraper(name=stockInfo['name'], isin=stockInfo['isin'],
                            currency=stockInfo['currency'], wkn=stockInfo['wkn'],
                            boerse_name=stockInfo['boerse_name'], typ=stockInfo['typ'],
                            avan_ticker=stockInfo['avan_ticker'])
        # TODO hier würde vermutlich eher ne liste an scrapern/requestern
        # übergeben werden, da verschiedene optionen
        # welche tabelle wo rein kommt entweder hier mit rein geben
        # oder database.Connector kann das selber zB aus Schema raus lesen
        self._conn.updateYearTables(self._scraper, stockId)
        self._conn.updateDateTables(self._scraper, stockId)
        self._conn.updateDayTables(self._scraper, stockId)


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

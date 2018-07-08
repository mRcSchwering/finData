# This Python file uses the following encoding: utf-8

# TODO methoden und init der Klassen testen
# TODO date types sollten eigentlich aus sql geladen werden
# TODO yearly und daily könnten in table namen encoded werden
# TODO constriants (zB currency) sollten in sql definiert sein

# TODO scraper sollte schema auch laden
# -> dann direkt die richtigen colnames nehmen
# -> diese ganzen scheiß conversions werden überfrlüssig


class SchemaInit(Schema):

    # name of the schema
    name = "findata_init"

    # tables which are updated daily, the rest is considered yearly
    daily_updates = ['hist']

    # non-numeric column types as they will be in DB schema
    date_columns = ['datum']
    int_columns = ['year']

    # column definitions as in DB schema
    tables = {
        'guv': ['stock_id', 'year', 'umsatz', 'bruttoergeb', 'EBIT', 'EBT', 'jahresueber', 'dividendena'],
        'bilanz': ['stock_id', 'year', 'umlaufvermo', 'anlagevermo', 'sum_aktiva', 'kurzfr_verb', 'langfr_verb', 'gesamt_verb', 'eigenkapita', 'sum_passiva', 'eigen_quote', 'fremd_quote'],
        'kennza': ['stock_id', 'year', 'gewinn_verw', 'gewinn_unvw', 'umsatz', 'buchwert', 'dividende', 'KGV', 'KBV', 'KUV'],
        'rentab': ['stock_id', 'year', 'umsatzren', 'eigenkapren', 'geskapren', 'dividren'],
        'person': ['stock_id', 'year', 'personal', 'aufwand', 'umsatz', 'gewinn'],
        'marktk': ['stock_id', 'year', 'zahl_aktien', 'marktkapita'],
        'divid': ['stock_id', 'datum', 'dividende', 'veraenderu', 'rendite'],
        'hist': ['stock_id', 'datum', 'open', 'high', 'low', 'close', 'adj_close', 'volume', 'divid_amt', 'split_coef']
    }

    # from scraper table id to name as in DB schema for each table
    conversions = {
        'guv': [
            {'id': 'Umsatz', 'name': 'umsatz'},
            {'id': 'Bruttoergebnis', 'name': 'bruttoergeb'},
            {'id': 'Operatives Ergebnis (EBIT)', 'name': 'EBIT'},
            {'id': 'Ergebnis vor Steuer (EBT)', 'name': 'EBT'},
            {'id': 'Jahresüberschuss', 'name': 'jahresueber'},
            {'id': 'Dividendenausschüttung', 'name': 'dividendena'}
        ],
        'bilanz': [
            {'id': 'Umlaufvermögen', 'name': 'umlaufvermo'},
            {'id': 'Anlagevermögen', 'name': 'anlagevermo'},
            {'id': 'Summe Aktiva', 'name': 'sum_aktiva'},
            {'id': 'Kurzfristige Verbindlichkeiten', 'name': 'kurzfr_verb'},
            {'id': 'Langfristige Verbindlichkeiten', 'name': 'langfr_verb'},
            {'id': 'Gesamtverbindlichkeiten', 'name': 'gesamt_verb'},
            {'id': 'Eigenkapital', 'name': 'eigenkapita'},
            {'id': 'Summe Passiva', 'name': 'sum_passiva'},
            {'id': 'Eigenkapitalquote', 'name': 'eigen_quote'},
            {'id': 'Fremdkapitalquote', 'name': 'fremd_quote'}
        ],
        'kennza': [
            {'id': 'Gewinn je Aktie (verwässert)', 'name': 'gewinn_verw'},
            {'id': 'Gewinn je Aktie (unverwässert)', 'name': 'gewinn_unvw'},
            {'id': 'Umsatz je Aktie', 'name': 'umsatz'},
            {'id': 'Buchwert je Aktie', 'name': 'buchwert'},
            {'id': 'Dividende je Aktie', 'name': 'dividende'},
            {'id': 'KGV (Kurs-Gewinn-Verhältnis)', 'name': 'KGV'},
            {'id': 'KBV (Kurs-Buchwert-Verhältnis)', 'name': 'KBV'},
            {'id': 'KUV (Kurs-Umsatz-Verhältnis)', 'name': 'KUV'}
        ],
        'rentab': [
            {'id': 'Umsatzrendite', 'name': 'umsatzren'},
            {'id': 'Eigenkapitalrendite', 'name': 'eigenkapren'},
            {'id': 'Gesamtkapitalrendite', 'name': 'geskapren'},
            {'id': 'Dividendenrendite', 'name': 'dividren'}
        ],
        'person': [
            {'id': 'Personal am Jahresende', 'name': 'personal'},
            {'id': 'Personalaufwand in Mio.', 'name': 'aufwand'},
            {'id': 'Umsatz je Mitarbeiter', 'name': 'umsatz'},
            {'id': 'Gewinn je Mitarbeiter', 'name': 'gewinn'}
        ],
        'marktk': [
            {'id': 'Anzahl der Aktien', 'name': 'zahl_aktien'},
            {'id': 'Marktkapitalisierung', 'name': 'marktkapita'}
        ],
        'divid': [
            {'id': 'Datum', 'name': 'datum'},
            {'id': 'Dividende', 'name': 'dividende'},
            {'id': 'Veränderung', 'name': 'veraenderu'},
            {'id': 'Rendite', 'name': 'rendite'}
        ],
        'hist': [
            {'id': 'datum', 'name': 'datum'},
            {'id': '1. open', 'name': 'open'},
            {'id': '2. high', 'name': 'high'},
            {'id': '3. low', 'name': 'low'},
            {'id': '4. close', 'name': 'close'},
            {'id': '5. adjusted close', 'name': 'adj_close'},
            {'id': '6. volume', 'name': 'volume'},
            {'id': '7. dividend amount', 'name': 'divid_amt'},
            {'id': '8. split coefficient', 'name': 'split_coef'}
        ]
    }

    def __init__(self):
        super().__init__()


class Schema(object):

    # name of the schema
    name = ''

    # tables which are updated daily, the rest is considered yearly
    daily_updates = ['']

    # non-numeric column types as they will be in DB schema
    date_columns = ['']
    int_columns = ['']

    # column definitions as in DB schema
    tables = {'table_name': ['col_name']}

    # from scraper table id to name as in DB schema for each table
    conversions = {'table_name': [{'id': 'scraper_id', 'name': 'col_name'}]}

    def __init__(self):
        tabs = [tab for tab in self.tables]
        convs = [tab for tab in self.conversions]
        if set(tabs) != set(convs):
            raise ValueError('Definitions for tables and conversions do not match')

    def table(self, name):
        if name not in [tab for tab in self.tables]:
            raise ValueError('table %s not defined in schema %s' %
                             (name, self.name))
        update_rate = 'daily' if name in self.daily_updates else 'yearly'
        cols = {key: Schema.getType(key) for key in self.tables.get(name)}
        return Table(name, update_rate, cols)

    def listTables(self):
        return [tab for tab in self.tables]

    @classmethod
    def getType(cls, col_name):
        if col_name in cls.date_columns:
            return 'date'
        if col_name in cls.int_columns:
            return 'int'
        return 'numeric'


class Table(object):

    def __init__(self, table_name, update_rate, column_types):
        self.name = table_name
        self.update_rate = update_rate
        self._column_types = column_types

    def column(self, name):
        if name not in [col for col in self._column_types]:
            raise ValueError('column %s not defined in table %s' %
                             (name, self.name))
        return Column(name, self._column_types.get(name))

    def listColumns(self):
        return [col for col in self._column_types]


class Column(object):

    def __init__(self, col_name, col_type):
        self.name = col_name
        self.type = col_type


c = SchemaInit()
c.name
c.listTables()
tab = c.table('divid')
tab.name
tab.update_rate
tab.listColumns()
col = tab.column('datum')
col.name
col.type

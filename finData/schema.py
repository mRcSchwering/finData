# This Python file uses the following encoding: utf-8
from finData.aschema import ASchema

# TODO scraper sollte schema auch laden
# -> dann direkt die richtigen colnames nehmen
# -> diese ganzen scheiß conversions werden überfrlüssig


class Schema(ASchema):

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

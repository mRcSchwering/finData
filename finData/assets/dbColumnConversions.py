class DBColumnConversions(object):

    dividend_yearly = [
        {'from': 'Datum', 'to': 'datum', 'type': 'other'},
        {'from': 'Dividende', 'to': 'dividende', 'type': 'num'},
        {'from': 'Veränderung', 'to': 'veraenderu', 'type': 'num'},
        {'from': 'Rendite', 'to': 'rendite', 'type': 'num'}
    ]

    fundamental_yearly = [
        {'from': 'Anzahl der Aktien', 'to': 'zahl_aktien', 'type': 'int'},
        {'from': 'Marktkapitalisierung', 'to': 'marktkapita', 'type': 'num'},
        {'from': 'Umsatzrendite', 'to': 'umsatzren', 'type': 'num'},
        {'from': 'Eigenkapitalrendite', 'to': 'eigenkapren', 'type': 'num'},
        {'from': 'Gesamtkapitalrendite', 'to': 'geskapren', 'type': 'num'},
        {'from': 'Dividendenrendite', 'to': 'dividren', 'type': 'num'},
        {'from': 'Umsatz', 'to': 'umsatz', 'type': 'int'},
        {'from': 'Bruttoergebnis', 'to': 'bruttoergeb', 'type': 'int'},
        {'from': 'Operatives Ergebnis (EBIT)', 'to': 'EBIT', 'type': 'int'},
        {'from': 'Ergebnis vor Steuer (EBT)', 'to': 'EBT', 'type': 'int'},
        {'from': 'Jahresüberschuss', 'to': 'jahresueber', 'type': 'int'},
        {'from': 'Dividendenausschüttung', 'to': 'dividendena', 'type': 'int'},
        {'from': 'Gewinn je Aktie (unverwässert)', 'to': 'gewinn_unvw', 'type': 'num'},
        {'from': 'Gewinn je Aktie (verwässert)', 'to': 'gewinn_verw', 'type': 'num'},
        {'from': 'Umsatz je Aktie', 'to': 'umsatz_a', 'type': 'num'},
        {'from': 'Buchwert je Aktie', 'to': 'buchwert', 'type': 'num'},
        {'from': 'Dividende je Aktie', 'to': 'dividende', 'type': 'num'},
        {'from': 'KGV (Kurs-Gewinn-Verhältnis)', 'to': 'KGV', 'type': 'num'},
        {'from': 'KBV (Kurs-Buchwert-Verhältnis)', 'to': 'KBV', 'type': 'num'},
        {'from': 'KUV (Kurs-Umsatz-Verhältnis)', 'to': 'KUV', 'type': 'num'},
        {'from': 'Personal am Jahresende', 'to': 'personal', 'type': 'int'},
        {'from': 'Personalaufwand in Mio.', 'to': 'pers_aufw', 'type': 'num'},
        {'from': 'Umsatz je Mitarbeiter', 'to': 'umsatz_m', 'type': 'num'},
        {'from': 'Gewinn je Mitarbeiter', 'to': 'gewinn_m', 'type': 'num'},
        {'from': 'Umlaufvermögen', 'to': 'umlaufvermo', 'type': 'num'},
        {'from': 'Anlagevermögen', 'to': 'anlagevermo', 'type': 'num'},
        {'from': 'Summe Aktiva', 'to': 'sum_aktiva', 'type': 'num'},
        {'from': 'Kurzfristige Verbindlichkeiten', 'to': 'kurzfr_verb', 'type': 'num'},
        {'from': 'Langfristige Verbindlichkeiten', 'to': 'langfr_verb', 'type': 'num'},
        {'from': 'Gesamtverbindlichkeiten', 'to': 'gesamt_verb', 'type': 'num'},
        {'from': 'Eigenkapital', 'to': 'eigenkapita', 'type': 'num'},
        {'from': 'Summe Passiva', 'to': 'sum_passiva', 'type': 'num'},
        {'from': 'Eigenkapitalquote', 'to': 'eigen_quote', 'type': 'num'},
        {'from': 'Fremdkapitalquote', 'to': 'fremd_quote', 'type': 'num'}
    ]

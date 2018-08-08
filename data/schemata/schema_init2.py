# This Python file uses the following encoding: utf-8
import psycopg2
from psycopg2.extensions import AsIs


def schema_init2(schema_name, conn):
    with conn.cursor() as cur:
            cur.execute("""CREATE SCHEMA IF NOT EXISTS %(schema_name)s""",
                        {'schema_name': AsIs(schema_name)})

            cur.execute("""
                CREATE TABLE IF NOT EXISTS %(schema_name)s.stock (
                  id          SERIAL PRIMARY KEY,
                  name        VARCHAR(50) NOT NULL,
                  isin        VARCHAR(50) UNIQUE NOT NULL,
                  currency    VARCHAR(5) NOT NULL,
                  boerse_name VARCHAR(50) UNIQUE NOT NULL,
                  avan_ticker VARCHAR(50) UNIQUE NOT NULL
                );
            """, {'schema_name': AsIs(schema_name)})

            cur.execute("""
                CREATE TABLE IF NOT EXISTS %(schema_name)s.fundamental_yearly (
                  id          SERIAL PRIMARY KEY,
                  stock_id    INTEGER REFERENCES %(schema_name)s.stock ( id ),
                  jahr        INTEGER NOT NULL,
                  umsatz      FLOAT,      -- in millionen EUR
                  bruttoergeb FLOAT,      -- in millionen EUR
                  EBIT        FLOAT,      -- in millionen EUR
                  EBT         FLOAT,      -- in millionen EUR
                  jahresueber FLOAT,      -- in millionen EUR
                  dividendena FLOAT,      -- in millionen EUR
                  umlaufvermo FLOAT,      -- in millionen EUR
                  anlagevermo FLOAT,      -- in millionen EUR
                  sum_aktiva  FLOAT,      -- in millionen EUR
                  kurzfr_verb FLOAT,      -- in millionen EUR
                  langfr_verb FLOAT,      -- in millionen EUR
                  gesamt_verb FLOAT,      -- in millionen EUR
                  eigenkapita FLOAT,      -- in millionen EUR
                  sum_passiva FLOAT,      -- in millionen EUR
                  eigen_quote FLOAT,      -- in percent
                  fremd_quote FLOAT,      -- in percent
                  gewinn_verw FLOAT,      -- je Aktie
                  gewinn_unvw FLOAT,      -- je Aktie
                  umsatz_a    FLOAT,      -- je Aktie
                  buchwert    FLOAT,      -- je Aktie
                  dividende   FLOAT,      -- je Aktie
                  KGV         FLOAT,      -- Kurs-Gewinn-Verh
                  KBV         FLOAT,      -- Kurs-Buchwert-Verh
                  KUV         FLOAT,      -- Kurs-Umsatz-Verh
                  umsatzren   FLOAT,      -- in percent
                  eigenkapren FLOAT,      -- in percent
                  geskapren   FLOAT,      -- in percent
                  dividren    FLOAT,      -- in percent
                  personal    INTEGER,    -- am Jahresende
                  pers_aufw   FLOAT,      -- Personalaufwand in Mio
                  umsatz_m    FLOAT,      -- je Mitarbeiter
                  gewinn_m    FLOAT,      -- je Mitarbeiter
                  zahl_aktien FLOAT,      --in thousands
                  marktkapita FLOAT       -- in Mio Euro
                );
            """, {'schema_name': AsIs(schema_name)})

            cur.execute("""
                CREATE TABLE IF NOT EXISTS %(schema_name)s.divid_yearly (
                  id          SERIAL PRIMARY KEY,
                  stock_id    INTEGER REFERENCES %(schema_name)s.stock ( id ),
                  datum       DATE NOT NULL,
                  dividende   FLOAT,
                  veraenderu  FLOAT,     -- in percent
                  rendite     FLOAT      -- in percent
                );
            """, {'schema_name': AsIs(schema_name)})

            cur.execute("""
                CREATE TABLE IF NOT EXISTS %(schema_name)s.hist_daily (
                  id          SERIAL PRIMARY KEY,
                  stock_id    INTEGER REFERENCES %(schema_name)s.stock ( id ),
                  datum       DATE NOT NULL,
                  open        FLOAT,
                  high        FLOAT,
                  low         FLOAT,
                  close       FLOAT,
                  adj_close   FLOAT,
                  volume      INTEGER,
                  divid_amt   FLOAT,
                  split_coef  FLOAT
                );
            """, {'schema_name': AsIs(schema_name)})

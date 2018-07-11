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
                  umsatz      INTEGER,    -- in millionen EUR
                  bruttoergeb INTEGER,    -- in millionen EUR
                  EBIT        INTEGER,    -- in millionen EUR
                  EBT         INTEGER,    -- in millionen EUR
                  jahresueber INTEGER,    -- in millionen EUR
                  dividendena INTEGER,    -- in millionen EUR
                  umlaufvermo FLOAT,      -- in millionen EUR
                  anlagevermo FLOAT,      -- in millionen EUR
                  sum_aktiva  FLOAT,      -- in millionen EUR
                  kurzfr_verb FLOAT,      -- in millionen EUR
                  langfr_verb FLOAT,      -- in millionen EUR
                  gesamt_verb FLOAT,      -- in millionen EUR
                  eigenkapita FLOAT,      -- in millionen EUR
                  sum_passiva FLOAT,      -- in millionen EUR
                  eigen_quote DECIMAL(5, 2), -- in percent
                  fremd_quote DECIMAL(5, 2), -- in percent
                  gewinn_verw DECIMAL(5,2),  -- je Aktie
                  gewinn_unvw DECIMAL(5,2),  -- je Aktie
                  umsatz      DECIMAL(5,2),  -- je Aktie
                  buchwert    DECIMAL(5,2),  -- je Aktie
                  dividende   DECIMAL(5,2),  -- je Aktie
                  KGV         DECIMAL(5,2),  -- Kurs-Gewinn-Verh
                  KBV         DECIMAL(5,2),  -- Kurs-Buchwert-Verh
                  KUV         DECIMAL(5,2),  -- Kurs-Umsatz-Verh
                  umsatzren   DECIMAL(5,2),  -- in percent
                  eigenkapren DECIMAL(5,2),  -- in percent
                  geskapren   DECIMAL(5,2),  -- in percent
                  dividren    DECIMAL(5,2),  -- in percent
                  personal    INTEGER,       -- am Jahresende
                  aufwand     FLOAT,         -- Personalaufwand in Mio
                  umsatz      FLOAT,         -- je Mitarbeiter
                  gewinn      FLOAT,         -- je Mitarbeiter
                  zahl_aktien INTEGER,
                  marktkapita FLOAT   -- in Mio Euro
                );
            """, {'schema_name': AsIs(schema_name)})

            cur.execute("""
                CREATE TABLE IF NOT EXISTS %(schema_name)s.divid_yearly (
                  id          SERIAL PRIMARY KEY,
                  stock_id    INTEGER REFERENCES %(schema_name)s.stock ( id ),
                  datum       DATE NOT NULL,
                  dividende   DECIMAL(5, 2),
                  veraenderu  DECIMAL(5, 2),   -- in percent
                  rendite     DECIMAL(5, 2)    -- in percent
                );
            """, {'schema_name': AsIs(schema_name)})

            cur.execute("""
                CREATE TABLE IF NOT EXISTS %(schema_name)s.hist_daily (
                  id          SERIAL PRIMARY KEY,
                  stock_id    INTEGER REFERENCES %(schema_name)s.stock ( id ),
                  datum       DATE NOT NULL,
                  open        DECIMAL(7, 2),
                  high        DECIMAL(7, 2),
                  low         DECIMAL(7, 2),
                  close       DECIMAL(7, 2),
                  adj_close   DECIMAL(7, 2),
                  volume      INTEGER,
                  divid_amt   DECIMAL(5, 2),
                  split_coef  DECIMAL(5, 2)
                );
            """, {'schema_name': AsIs(schema_name)})

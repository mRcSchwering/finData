# This Python file uses the following encoding: utf-8
import psycopg2
from psycopg2.extensions import AsIs


def create_schema(db_name, schema_name, user, host, port, password=""):
    if password == "":
        conn = psycopg2.connect(dbname=db_name, user=user, host=host, port=port)
    else:
        conn = psycopg2.connect(dbname=db_name, user=user, host=host, port=port, password=password)

    with conn:
        with conn.cursor() as cur:
                cur.execute("""CREATE SCHEMA IF NOT EXISTS %(schema_name)s""",
                            {'schema_name': AsIs(schema_name)})

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS %(schema_name)s.stock (
                      id          INTEGER PRIMARY KEY,
                      name        VARCHAR(50) NOT NULL,
                      isin        VARCHAR(50) UNIQUE NOT NULL,
                      wkn         VARCHAR(50) UNIQUE NOT NULL,
                      typ         VARCHAR(10) NOT NULL,
                      currency    VARCHAR(5) NOT NULL,
                      boerse_name VARCHAR(50) UNIQUE NOT NULL,
                      avan_ticker VARCHAR(50) UNIQUE NOT NULL
                    );
                """, {'schema_name': AsIs(schema_name)})

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS %(schema_name)s.guv (
                      id          INTEGER PRIMARY KEY,
                      stock_id    INTEGER REFERENCES %(schema_name)s.stock ( id ),
                      year        INTEGER NOT NULL,
                      umsatz      INTEGER,    -- in millionen EUR
                      bruttoergeb INTEGER,    -- in millionen EUR
                      EBIT        INTEGER,    -- in millionen EUR
                      EBT         INTEGER,    -- in millionen EUR
                      jahresueber INTEGER,    -- in millionen EUR
                      dividendena INTEGER     -- in millionen EUR
                    );
                """, {'schema_name': AsIs(schema_name)})

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS %(schema_name)s.bilanz (
                      id          INTEGER PRIMARY KEY,
                      stock_id    INTEGER REFERENCES %(schema_name)s.stock ( id ),
                      year        INTEGER NOT NULL,
                      umlaufvermo FLOAT,      -- in millionen EUR
                      anlagevermo FLOAT,      -- in millionen EUR
                      sum_aktiva  FLOAT,      -- in millionen EUR
                      kurzfr_verb FLOAT,      -- in millionen EUR
                      langfr_verb FLOAT,      -- in millionen EUR
                      gesamt_verb FLOAT,      -- in millionen EUR
                      eigenkapita FLOAT,      -- in millionen EUR
                      sum_passiva FLOAT,      -- in millionen EUR
                      eigen_quote DECIMAL(5, 2), -- in percent
                      fremd_quote DECIMAL(5, 2)  -- in percent
                    );
                """, {'schema_name': AsIs(schema_name)})

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS %(schema_name)s.kennza (
                      id          INTEGER PRIMARY KEY,
                      stock_id    INTEGER REFERENCES %(schema_name)s.stock ( id ),
                      year        INTEGER NOT NULL,
                      gewinn_verw DECIMAL(5,2),  -- je Aktie
                      gewinn_unvw DECIMAL(5,2),  -- je Aktie
                      umsatz      DECIMAL(5,2),  -- je Aktie
                      buchwert    DECIMAL(5,2),  -- je Aktie
                      dividende   DECIMAL(5,2),  -- je Aktie
                      KGV         DECIMAL(5,2),  -- Kurs-Gewinn-Verh
                      KBV         DECIMAL(5,2),  -- Kurs-Buchwert-Verh
                      KUV         DECIMAL(5,2)   -- Kurs-Umsatz-Verh
                    );
                """, {'schema_name': AsIs(schema_name)})

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS %(schema_name)s.rentab (
                      id          INTEGER PRIMARY KEY,
                      stock_id    INTEGER REFERENCES %(schema_name)s.stock ( id ),
                      year        INTEGER NOT NULL,
                      umsatzren   DECIMAL(5,2),  -- in percent
                      eigenkapren DECIMAL(5,2),  -- in percent
                      geskapren   DECIMAL(5,2),  -- in percent
                      dividren    DECIMAL(5,2)   -- in percent
                    );
                """, {'schema_name': AsIs(schema_name)})

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS %(schema_name)s.person (
                      id          INTEGER PRIMARY KEY,
                      stock_id    INTEGER REFERENCES %(schema_name)s.stock ( id ),
                      year        INTEGER NOT NULL,
                      personal    INTEGER,       -- am Jahresende
                      aufwand     FLOAT,         -- Personalaufwand in Mio
                      umsatz      FLOAT,         -- je Mitarbeiter
                      gewinn      FLOAT          -- je Mitarbeiter
                    );
                """, {'schema_name': AsIs(schema_name)})

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS %(schema_name)s.marktk (
                      id          INTEGER PRIMARY KEY,
                      stock_id    INTEGER REFERENCES %(schema_name)s.stock ( id ),
                      year        INTEGER NOT NULL,
                      zahl_aktien INTEGER,
                      marktkapita FLOAT   -- in Mio Euro
                    );
                """, {'schema_name': AsIs(schema_name)})

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS %(schema_name)s.divid (
                      id          INTEGER PRIMARY KEY,
                      stock_id    INTEGER REFERENCES %(schema_name)s.stock ( id ),
                      datum       DATE NOT NULL,
                      dividende   DECIMAL(5, 2),
                      veraenderu  DECIMAL(5, 2),   -- in percent
                      rendite     DECIMAL(5, 2)    -- in percent
                    );
                """, {'schema_name': AsIs(schema_name)})

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS %(schema_name)s.hist (
                      id          INTEGER PRIMARY KEY,
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

    conn.close()


def drop_schema(db_name, schema_name, user, host, port, password=""):
    if password == "":
        conn = psycopg2.connect(dbname=db_name, user=user, host=host, port=port)
    else:
        conn = psycopg2.connect(dbname=db_name, user=user, host=host, port=port, password=password)

    with conn:
        with conn.cursor() as cur:
                cur.execute("""DROP SCHEMA IF EXISTS %(schema_name)s CASCADE""",
                            {'schema_name': AsIs(schema_name)})

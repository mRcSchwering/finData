# This Python file uses the following encoding: utf-8
"""Integration tests

Detailed Description
"""

import psycopg2 as pg


def _log(msg):
    print("\n\n" + msg + "\n" + "#" * 40 + "\n")


def main():
    conn = pg.connect(dbname="findata", user="postgres", host="server", port="5432")

    _log("Show databases have findata")
    with conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT datname FROM pg_database""")
            res = cur.fetchall()
            print(res)
            fd = [d[0] for d in res if d[0] == 'findata']
            assert len(fd) == 1
    conn.close()

    [d[0] for d in data if d[0] == 'findata']


if __name__ == "__main__":
    main()

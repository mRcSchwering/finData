# This Python file uses the following encoding: utf-8
from unittest.mock import patch
from unittest.mock import MagicMock
import unittest
import sys
import io


# mocking DB connection
def mockDBconnect(mockDB):
    cur = MagicMock()
    cur.__enter__ = MagicMock(return_value=mockDB)
    cur.__exit__ = MagicMock(return_value=False)
    con = MagicMock()
    con.cursor = MagicMock(return_value=cur)
    conn = MagicMock()
    conn.__enter__ = MagicMock(return_value=con)
    conn.__exit__ = MagicMock(return_value=False)
    return conn


# extracting cursor from mocked connection
def getCursor(x):
    return x.conn.__enter__().cursor().__enter__()


# helper for silencing
class catchStdout:

    def __enter__(self):
        capture = io.StringIO()
        sys.stdout = capture
        return capture

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__

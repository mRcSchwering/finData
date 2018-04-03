# This Python file uses the following encoding: utf-8
"""Short Description.

Detailed Description
"""

import os
import re
import json
import psycopg2
import datetime as dt


class Loader(object):
    host = 'www.boerse.de'

    def __init__(self, name, isTest=False):
        self.name = str(name)
        self.isTest = isTest


def main():
    pass

# This Python file uses the following encoding: utf-8
import datetime as dt


class History(object):
    """
    Handling timeline information for a Stock object

    today   date today

    table   set table to generate update information for table
    isNew   test if a given time point is new
    """

    #update limit in years
    limit = 20

    def __init__(self, schema, stock):
        if stock._id is None:
            raise AttributeError('Set Stock object first with "exists" method')
        self._schema = schema
        self._stock = stock
        self.today = dt.date.today()
        self._table = None
        self.last_update = None
        self.name = None
        self._type = None
        self.days_missing = None
        self.years_missing = None
        self.update_rate = None

    def table(self, name):
        """
        Set table to generate update information about it. Sets attributes:

        name            name of set table
        last_update     latest timepoint for stock in this table
        days_missing    time delta between today and the last update
        years_missing   number of years bewteen today and last update
        update_rate     update rate of selected table
        """
        if name not in self._schema.tables:
            raise ValueError(
                'Table %s not defined in schema %s' % (name, self._schema.name))
        self.name = name
        self._table = self._schema.table(name)
        self.last_update = self._getLastUpdate()
        self._type = self._getType()
        self.years_missing = self._getMissingYears()
        self.days_missing = self._getMissingDays()
        self.update_rate = self._table.update_rate

    def isNew(self, timepoint):
        """
        Is given date or year new for stock in table?

        A table needs to be set.
        Whether it is new, is decided on the update rate of that table.
        """
        if True not in [isinstance(timepoint, d) for d in [int, dt.date]]:
            raise ValueError('Provide year as integer or date as dt.date')
        if self.update_rate == 'daily' and isinstance(timepoint, int):
            raise ValueError('Provide date, this table has a daily update rate')
        if self._table is None:
            raise AttributeError('Set table first with "table" method')

        last_update = self.last_update
        if isinstance(timepoint, dt.date):
            if self._type == 'date':
                time_delta = timepoint - last_update
                years_delta = timepoint.year - last_update.year
            if self._type == 'year':
                time_delta = timepoint - dt.date(last_update, 1, 1)
                years_delta = timepoint.year - last_update
        if isinstance(timepoint, int):
            if self._type == 'date':
                time_delta = dt.date(timepoint, 1, 1) - last_update
                years_delta = timepoint - last_update.year
            if self._type == 'year':
                time_delta = dt.date(timepoint, 1, 1) - dt.date(last_update, 1, 1)
                years_delta = timepoint - last_update

        if self.update_rate == 'yearly':
            return years_delta > 0
        if self.update_rate == 'daily':
            return time_delta > dt.timedelta(0)
        raise ArithmeticError('Something went wrong in comparing timepoints')

    def _getLastUpdate(self):
        return self._table.lastUpdate(self._stock._id)

    def _getType(self):
        typ = self._table.column(self._table.time_column).type
        if typ == 'date':
            return 'date'
        if typ == 'integer':
            return 'year'
        raise AttributeError("Can't figure out time type. Unclear timepoint column type.")

    def _getMissingYears(self):
        if self.last_update is None:
            return self.limit
        if self._type == 'year':
            update_year = self.last_update
        if self._type == 'date':
            update_year = self.last_update.year
        return self.today.year - update_year

    def _getMissingDays(self):
        if self.last_update is None:
            return self.today - dt.date(self.today.year - self.limit, 1, 1)
        if self._type == 'year':
            update_day = dt.date(self.last_update, 1, 1)
        if self._type == 'date':
            update_day = self.last_update
        return self.today - update_day

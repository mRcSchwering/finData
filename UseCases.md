

### 1 Insert Stock Symbol

- enter stock (+isin, wkn, urls...) in schema.stock
- check variables urls make sense...
- if it exists, do not enter again, give feedback
- possibility to provide many stocks
- notify which ones were entered, which already existed


### 2 Update Stocks' Data

- for all stocks in table schema.stocks
- check if new data is available (somehow, maybe by date)
- if so, update it (-> requests/scrape -> insert new data)
- if no data at all, or last entered is more then 100 days old -> make heavy API call (AlphaVantage), otherwise light API call
- feedback what was entered (overviewish)

### 3 View Data Quality Report

- some kind of overview about data quality
- especially missing data
- for hist data, beginning and end of year is important (for return calculation)
- some heuristic that guesses first and last trading day
- bad quality data should be highlighted in a way that follow up is easy

### 4 Enter custom PSQL statement

- some method that lets you use your custom sql statement (maybe as string)
- avoiding entering doubles must be ensured (maybe the DB's UNIQUEs are enough)

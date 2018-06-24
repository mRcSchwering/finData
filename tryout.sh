

# normal: 02:10
# prebuilt containers: 02:01



# TODO: integration test schreiben
./helper.sh start server

# delete Deutsche Börse
psql \
  -h 127.0.0.1 \
  -p 5432 \
  -U postgres \
  findata \
  -c "SELECT id FROM testdb.stock WHERE name = 'Deutsche Börse'"
id=13
psql \
  -h 127.0.0.1 \
  -p 5432 \
  -U postgres \
  findata \
  -c "DELETE FROM testdb.guv WHERE stock_id = $id"
psql \
  -h 127.0.0.1 \
  -p 5432 \
  -U postgres \
  findata \
  -c "DELETE FROM testdb.bilanz WHERE stock_id = $id"
psql \
  -h 127.0.0.1 \
  -p 5432 \
  -U postgres \
  findata \
  -c "DELETE FROM testdb.rentab WHERE stock_id = $id"
psql \
  -h 127.0.0.1 \
  -p 5432 \
  -U postgres \
  findata \
  -c "DELETE FROM testdb.person WHERE stock_id = $id"
psql \
  -h 127.0.0.1 \
  -p 5432 \
  -U postgres \
  findata \
  -c "DELETE FROM testdb.marktk WHERE stock_id = $id"
psql \
  -h 127.0.0.1 \
  -p 5432 \
  -U postgres \
  findata \
  -c "DELETE FROM testdb.kennza WHERE stock_id = $id"
psql \
  -h 127.0.0.1 \
  -p 5432 \
  -U postgres \
  findata \
  -c "DELETE FROM testdb.divid WHERE stock_id = $id"
psql \
  -h 127.0.0.1 \
  -p 5432 \
  -U postgres \
  findata \
  -c "DELETE FROM testdb.hist WHERE stock_id = $id"
psql \
  -h 127.0.0.1 \
  -p 5432 \
  -U postgres \
  findata \
  -c "DELETE FROM testdb.stock WHERE id = $id"

# insert again
python3 -m finData.connect \
  --schema testdb \
  --host "127.0.0.1" \
  --port 5432 \
  insert \
  "Deutsche Börse" "DE0005810055" "581005" "EUR" "Deutsche-Boerse-Aktie" "DB1.DE"
  # name ISIN WKN currency boerse_name avan_ticker

# nochmal ausführen -> not inserted, already exists

# update -> dieses updaten
python3 -m finData.connect \
  --schema testdb \
  --host "127.0.0.1" \
  --port 5432 \
  update

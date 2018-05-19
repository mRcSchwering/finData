# config.json

Any keys for development.
The relevant functions should look for the `config.json` first,
then for environment variables if they didn't find the key.

```
{
  "ALPHAVANTAGE_API_KEY": ""
}
```

# helper.sh

Helper for developing.
Use:
- `helper.sh test [<searchString>]` to run tests [filter for certain tests]
- `helper.sh start server` to start postgres server with volume attached
- `helper.sh connect` to psql into database
- `helper.sh stop server` to stop postgres server
- `helper.sh create <testSchemaName>` to create a test schema in database
- `helper.sh drop <testSchemaName>` to drop a test schema in database

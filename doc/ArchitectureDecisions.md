# Architectural Decisions


## finData entrypoint

The finData `Dockerfile` has an entrypoint `["python3", "-m"]`.
So all interactive functions have to be callable by module functions.
_E.g._ in the `.circleci/config.yml` integration testing is started by
`test.integration_test`.

Reasons were:
- save to use, more restriction how to use it, the app is not so much interactive (rather batch)
- convenient, eventually there will be only 3 or 4 functions that are being used anyway

**Note**
In circleci the docker executor with the _finData_ image ignores the _entrypoint_.
So here, the `.circleci/config.yml` still calls the smoke tests with `python3 -m unittest ...`.


## Database Docker Volume

The database will be a docker volume.
I thought about bind mounting it, but eventually didn't see a reason to not
use docker volume.
Seems more flexible.
I will use **Postgres** btw (no-brainer).

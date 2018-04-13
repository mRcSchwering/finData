# `build` Docker Image

If the build should be in a separate image (_e.g._ for integration tests)
you have to use a docker-in-docker setup in CircleCI (at least in the free one).

Basically define a _job_ starting with a docker image that has docker installed,
add your app, build a new docker image within that docker image, then push the
new image to _docker hub_ (or so).
Then you can define _jobs_ using that image as base image.

### Docker-In-Docker in CircleCI

To avoid conflicts using docker commands within a docker container
(which in turn was started by some host using the same docker commands)
CircleCI added a `setup_remote_docker` configuration.
So the following seems to work fine together:

```
version: 2
jobs:

  build:
    docker:
      - image: docker:17.05.0-ce-git
    steps:
      - checkout
      - setup_remote_docker:
          version: 17.11.0-ce
      - run: ...
```

### Push Build to Dockerhub (or so)

Next the image is build with whatever procedure.
To use the image later on it must be `push`ed to some **public** repository.
I'd say docker hub is an obvious choice.
Somewhere in the _project_ settings in the CircleCI UI you can set
secret environment variables for your password (_e.g._ `$DOCKERHUB_PASS`).

```
version: 2
jobs:

  build:
    docker:
      - image: docker:17.05.0-ce-git
    steps:
      - checkout
      - setup_remote_docker:
          version: 17.11.0-ce
      - run:
          name: Build myApp
          command: docker build -t "myName/cci-myApp_build:latest" .
      - run:
          name: Push myApp
          command: |
            docker login -u="$DOCKERHUB_USER" -p="$DOCKERHUB_PASS"
            docker push "myName/cci-myApp_build:latest"
```

### Use Build as Base Image

Finally the image can be used as base image for all following _jobs_.

```
version: 2
jobs:

  build:
    ...

  smoke:
    working_directory: /app
    docker:
      - image: myName/cci-myApp_build:latest
    steps:
      - run: python3 -m unittest discover -s test -v
    ...

  workflows:
    version: 2
    build_and_test:
      jobs:
        - build
        - smoke-scraper:
            requires:
              - build
```

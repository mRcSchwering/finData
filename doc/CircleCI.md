# `build` Docker Image

If the build should be in a separate image (_e.g._ for integration tests)
you have to use a docker-in-docker setup in CircleCI (at least in the free one).

Basically define a _job_ starting with a docker image that has docker installed,
add your app, build a new docker image within that docker image, then push the
new image to _docker hub_.
Then you can define _jobs_ using that image as base image.

### Docker-In-Docker in CircleCI

You have to tell docker to use the remote socker (from circleci).
There is a `setup_remote_docker` configuration for this.

```
version: 2
jobs:

  build:
    docker:
      - image: docker:18.03.0-ce-git
    steps:
      - checkout
      - setup_remote_docker
      - run: ...
```

### Push Build to Dockerhub

Next the image is build with whatever procedure.
To use the image later on it must be `push`ed to some **public** repository.
Somewhere in the _project_ settings in the CircleCI UI you can set
secret environment variables for your password (_e.g._ `$DOCKERHUB_PASS`).

```
version: 2
jobs:

  build:
    docker:
      - image: docker:18.03.0-ce-git
    steps:
      - checkout
      - setup_remote_docker
      - run:
          name: Build myApp
          command: docker build -t "myName/cci-myApp_build:latest" .
      - run:
          name: Push myApp
          command: |
            docker login -u="$DOCKERHUB_USER" -p="$DOCKERHUB_PASS"
            docker push "myName/cci-myApp_build:latest"
```

Circleci provides different options for caching and/or persisting an
environment but (at least in the free version) it is faster and
more straight forward to push/pull to a repo.

# Integration Tests

The easiest solution is to use docker-compose-in-docker.
So, a docker executor job that also has `docker-compose` and that starts
containers within a docker network.

### Docker-compose-in-Docker

We start with the usual `docker:18.03.0-ce-git`, install `docker-compose` on
top and set the remote docker socket.
It turned out that alpine doesn't like the `docker-compose` binary.
So unfortunately you end up with a base image like this.

```
FROM docker:18.03.0-ce-git
RUN apk --update add py2-pip
RUN pip install docker-compose
```

### Integration Test

Next, start your docker containers within their network with
`docker-compose up -d` and let them talk to each other.
Remember, the _server_ container probably needs a while to start up,
so let the _client_ container `sleep 5` or so before it starts to talk
to the server.

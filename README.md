[![codecov](https://codecov.io/gh/Hanagotchi/social/graph/badge.svg?token=KSFWCISJQO)](https://codecov.io/gh/Hanagotchi/social) [![Tests](https://github.com/Hanagotchi/social/actions/workflows/tests.yml/badge.svg)](https://github.com/Hanagotchi/social/actions/workflows/tests.yml) [![Linters](https://github.com/Hanagotchi/social/actions/workflows/linters.yml/badge.svg)](https://github.com/Hanagotchi/social/actions/workflows/linters.yml)

# Social Microservice

This is a microservice that provides information about social network.

## Documentation

- Swagger documentation: `http://localhost:PORT/docs`.
- ReDoc documentation: `http://localhost:PORT/redoc`.

Where `PORT` is the port where the microservice is running defined in the [env](.env) file.

## Environment Variables

Environment variables are defined in the [env.example](.env.example) file.

### Application Configuration
- `PORT`: The port number on which the application will run. Example value: `8081`.
- `LOGGING_LEVEL`: The logging level for the application. Example values: `DEBUG`, `INFO`.
- `TZ`: The timezone for the application. Example value: `America/Argentina/Buenos_Aires`.

### Mongo Database Connection
- `MONGO_URL`: The URL for connecting to the MongoDB database. Example value: `mongodb://localhost:27017`.
- `MONGO_PORT`: The port number of the MongoDB server. Example value: `27017`.
- `MONGO_INITDB_DATABASE`: The name of the database containing the data. Example value: `social_service`.

### External Services
- `USERS_SERVICE_URL`: The URL for communicating with the users microservice. Example value: `http://users:8082`. 

## MongoDB
This project uses MongoDB as the database. The script that is executed when initializing the database can be found within [./app/docker/init-mongodb.js](./app/docker/init-mongodb.js). This script creates the collections and inserts the initial data.

## Poetry

This project uses [Poetry](https://python-poetry.org/) to manage dependencies.

### Install Poetry

```$ pip install poetry```

### Install dependencies

```$ poetry install```

### Add new dependency

```$ poetry add <dependency>```

### Update dependencies

```$ poetry update```

### Poetry locks

After any change in pyproject.toml file (always execute this before installing):

```$ poetry lock```

## Docker

#### Build container

```$ docker-compose build```

#### Start services

```$ docker-compose up```

#### List images

```$ docker images```

#### Remove dangling images: 

When you run a docker-compose build, it creates a new image, but it doesn't remove the old one, so you can have a lot of images with the same name but different id. Then, you can remove all of them with the following command:

```$ docker rmi $(docker images -f dangling=true -q) -f```

#### Deep Cleaning - Free space on your disk
*Warning*: This will remove all containers, images, volumes and networks not used by at least one container.
Its *recommended* to run this command before docker-compose up to avoid problems.

```$ docker system prune -a --volumes```

#### Usage Instructions with Makefile
The repository includes a **Makefile** that encapsulates various commands used frequently in the project as targets. The targets are executed by invoking:

* **make \<target\>**:
The essential targets to start and stop the system are **docker-compose-up** and **docker-compose-down**, with the remaining targets being useful for debugging and troubleshooting.

Available targets are:
* **docker-compose-up**: Initializes the development environment (builds docker images for the server and client, initializes the network used by docker, etc.) and starts the containers of the applications that make up the project.
* **docker-compose-down**: Performs a `docker-compose stop` to stop the containers associated with the compose and then performs a `docker-compose down` to destroy all resources associated with the initialized project. It is recommended to execute this command at the end of each run to prevent the host machine's disk from filling up.
* **docker-compose-logs**: Allows viewing the current logs of the project. Use with `grep` to filter messages from a specific application within the compose.
* **docker-image**: Builds the images to be used. This target is used by **docker-compose-up**, so it can be used to test new changes in the images before starting the project.

## Testing

### With Poetry

After any change in pyproject.toml file (always execute this before installing):

```$ poetry lock```

Then, install the development dependencies:
```$ poetry install -E dev```

To run the tests:
```$ poetry run pytest app```

### With Docker

```$ docker build -t test-social -f Dockerfile.test . && docker run test-social && docker rmi test-social -f```

Or use the Makefile target:

```$ make docker-test```
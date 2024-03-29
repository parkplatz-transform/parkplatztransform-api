## Parkplatz Transform API

![Integration Tests](https://github.com/parkplatz-transform/parkplatztransform-api/workflows/test-integration/badge.svg)

### Relevant external documentation

| Name       | Documentation                                    | Role                |
| -----------| -------------------------------------------------|---------------------|
| FastAPI    | [docs](https://fastapi.tiangolo.com/)            | API Framework       |
| SQLAlchemy | [docs](https://docs.sqlalchemy.org/en/13/)       | ORM                 |
| Alembic    | [docs](https://alembic.sqlalchemy.org/en/latest/)| Database migrations |
| PostgresSQL| [docs](https://www.postgresql.org/)              | Database            |
| PostGIS    | [docs](https://postgis.net/documentation/)       | Geo Extensions      |

### Open API Documentation

Autogenerated API documentation can be found [here](https://api.xtransform.org/docs) as well as
[redoc here](https://api.xtransform.org/redoc)

### Authentication and Authorization

Authentication is done by generating a link and emailing it to a user. The user verifies they have access to the email address provided by clicking the link in the email.

Authorization is done once an email address is verified by an API endpoint. The verification endpoint will return a signed JWT, this can be provided in an `Authorization: Bearer XXX` header to make authorized requests.

See also: <br>
[Passwordless authentication](https://en.wikipedia.org/wiki/Passwordless_authentication)
<br/>
[Passwordless logins in Python](https://www.anthonycorletti.com/post/python-passwordless/)

### Local Development

If you would like to work on the backend, you can follow the steps bellow:

Clone the repository:
```shell
git clone git@github.com:theolampert/parkplatztransform-api.git && cd parkplatztransform-api
```

You will then need to create an `.env` file in the root directory of this project. It should look something like this:

```shell
SECRET_KEY=averysecretkey
DATABASE_URL=postgresql://postgres:postgres@postgres/postgres
# The following are optional and only required for testing email
MAILGUN_DOMAIN=<MAILGUN_DOMAIN>
MAILGUN_API_KEY=<MAILGUN_API_KEY> 
```

One way to run the API locally is by using docker and docker compose.

To build the containers and install dependencies:
```shell
docker-compose build
```

To start the database and python app:
```shell
docker-compose up
```

Now run the database migrations:
```shell
sh ./scripts/migrate.sh
```

The web server will be available [here](http://localhost:8023)

**Important**: Docker & docker compose configuration is not secure and optimised for local development, don't deploy the app using these settings.

If you prefer to run the app without using docker, make sure you have postgresql (with Postgis extension) running locally and set the appropriate value for the environment variable `DATABASE_URL`. You will need Python 3.9+ and Pip installed.
Run `pip install -r requirements.txt` in the root directory to install dependencies.

### Database Migrations

The project uses Alembic for generating some versioned migration boilerplate, however Alembic encourages that you inspect and edit these migration files to your needs.
A few helper scripts exist to run migrations scripts inside the docker containers.


To generate a new migration file based off of SQLAlchemy models:

```shell
sh ./scripts/make-migrations.sh
```

To migrate a database to its latest version run:
```shell
sh ./scripts/migrate.sh
```

__Caveats__: Changes to enums and `geoAlchemy2` fields currently require manual intervention.

### Tests

To run integration tests for the API endpoints run the following (requires docker & docker-compose):

```shell
sh ./scripts/test.sh
```

### Deployment

The application is currently deployed on Heroku and depends on the following third-party services:
- Mailgun API for sending emails contains verification links
- Heroku Postgres with the PostGIS extension installed
- Heroku Redis for session storage

These services should set their environment variables automatically, if not add them manually in the dashboard.

The application uses continuous integration and will automatically deploy the `main` branch on any commits.

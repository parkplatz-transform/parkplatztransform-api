### Parkplatz Transform

Park Platz Transform API, intended to be consumed by the Park Platz Transform app, admin and potential 3rd parties.

#### Technology Overview:

| Name       | Documentation                                                                                 |
| ----------------- | --------------------------------------------------------------------------------------- |
| FastAPI            | [docs](https://fastapi.tiangolo.com/)                   |
| PostgresSQL        | [docs](https://www.postgresql.org/)           |
| PostGIS | [docs](https://postgis.net/documentation/)                         |
| GraphQL | [docs](https://graphql.org/)                         |

#### Authentication:

In the current implementation the authentication system is implemented using a concept of "magic links" or "password less" auth.


A client makes a request with an email address and a JWT token is generated and signed by the server using a secret key. The JWT is delivered to the email address as part of a verification link.


An endpoint on the server verifies that a JWT was signed with the same secret key and matches an email given to that key. From then on, authenticated requests can be made with this JWT. Clients requesting access to protected GraphQL queries should include the JWT token as part of a `Authentication: Bearer <Token>` header. 

The key expires after 2 weeks and must be verified within two hours of being generated. There is currently no concept of roles, however this should be discussed.

↓ CreateUser Mutation with email parameter

↓ Generate signed token

↓ Email token verify link

↓ Verify token was signed by server in given time frame


#### Development:

Clients apps can likely develop against the production backend, however if you would like to work on the backend, you can follow the steps bellow:

You will need to create a `.env` file in the root directory of this project once you've cloned this repository. It should look something like the following:

```
SECRET_KEY=averysecretkey
DATABASE_URL=postgresql://postgres:postgres@postgres/postgres
MAILGUN_DOMAIN=<MAILGUN_DOMAIN>
MAILGUN_API_KEY=<MAILGUN_API_KEY>
```

The easiest way to run the API locally is by using docker and docker compose. Docker is setup for development only.
Simply run the following in the project directory:

```shell
docker-compose build
```
To build the containers and install dependencies

```shell
docker-compose up
```
To start the database and web server

#### Deployment

The application is currently deployed on Heroku and depends on the following third party services:
- Mailgun API for sending magic link emails
- Heroku Postgres with PostGIS extension installed

The application uses continuous integration and will automatically deploy the `main` branch on any commits.
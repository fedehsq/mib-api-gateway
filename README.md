# Message In a Bottle - API Gateway

[![Build Status](https://app.travis-ci.com/fedehsq/micro_mib.svg?token=sCUbEzotwbjEpdHdvWDb&branch=master)](https://app.travis-ci.com/fedehsq/micro_mib), coverage 90%

This is the source code of Message in a Bottle application, self project of *Advanced Software Engineering* course,
University of Pisa.

- The *squad id* is **9**
- The *team leader* is Francesco Kotopulos De Angelis

#### Members

|         Name and Surname         |              Email                  |
| ------------------------------   | ----------------------------------- |
| Federico Bernacca                | f.bernacca@studenti.unipi.it        |
| Paola Petri                      | p.petri1@studenti.unipi.it          |
| Nicolò Pierami                   | n.pierami@studenti.unipi.it         |
| Francesco Kotopulos De Angelis   | f.kotopulosdeange@studenti.unipi.it |
| Manfredo Facchini                | m.facchini1@studenti.unipi.it       |


## Instructions

### Initialisation

To setup the project initially you have to run these commands
inside the project's root.

`virtualenv -p python3 venv`

`source venv/bin/activate`

`pip install -r requirements.dev.txt`

### Run the project

To run the project you have to setup the flask environment,
you can do it by executing the following command:

`export FLASK_ENV=<environment-name>`

and now you can run the application

`flask run`

**WARNING**: the static contents are inside the directory nginx/static,
so if you want to run application without nginx you have to copy
the static directory inside mib folder.

#### Application Environments

The available environments are:

- debug
- development
- testing
- production

If you want to run the application you have to startup the redis
instance, using the command:

```shell script
cp env_file_example env_file
export FLASK_ENV=development
flask run
```

#### Python dotenv

Each time you start a new terminal session, you have to
set up all the environment variables that projects requires.
When the variables number increases, the procedures needed to run
the project becomes uncomfortable. 

To solve this problem we have introduced the python-dotenv dependency,
but only for development purposes.
You can create a file called `.env` that will be interpreted each time
that you run the python project.
Inside `.env` file you can store all variables that project requires.
The `.env` file **MUST NOT** be added to repository and must kept
local. You can find an example with `.env-example` file.

### Dependencies splitting

Each environment requires its dependency. For example
`production` env does not require the testing frameworks.
Also to keep the docker image clean and thin we have
to split the requirements in 2 files.

- `requirements.txt` is the base file.
- `requirements.dev.txt` extends base file and it contains all development requirements,
for example pytest.
- `requirements.prod.txt` extends base file and it contains the production requirements,
for example gunicorn and psycopg2.

**IMPORTANT:** the Docker image uses the only the production requirements.
### Run tests

To run all the tests, once downloaded, execute the following command:

run all microservices in their folder:

`virtualenv -p python3 venv`

`source venv/bin/activate`

`pip install -r requirements.dev.txt`

`export FLASK_ENV=development`

`bash run.sh`

then in this folder:

`python -m pytest`

You can also specify one or more specific test files, in order to run only those specific tests.
In case you also want to see the overall coverage of the tests, execute the following command:

`python -m pytest --cov=mib`

In order to know what are the lines of codes which are not covered by the tests, execute the command:

`python -m pytest --cov-report term-missing`

### Nginx and Gunicorn

Nginx will serve static contents directly and will use gunicorn
to serve app pages from flask wsgi.
You can start gunicorn locally with the command

`gunicorn --config gunicorn.conf.py wsgi:app`

**WARNING** gunicorn it's not able to read
the .env files, so you have to export the variable, for
example by issuing the command `source .env`.


### Docker compose

To run services with `docker-compose up`, first you
have to configure the environment variables
inside the env_file, and specify it with the parameter `--env-file`.
An example of env_file is added to repository and it's called
env_file_example.

**WARNING:** please do not track your env_file!

The complete command to run this service with docker is the following:

`docker-compose --env-file <your-env-file> up`

### Nginx orchestrator

We have created a specific documentation file for 
[nginx-orchestrator](./nginx-orchestrator/README.md)


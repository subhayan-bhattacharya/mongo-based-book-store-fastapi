# Description
A simple FastApi based rest api using mongo db as the backend

## Spinning up the service
We can use `docker-compose up` to get the service up and running


# Running tests
For running the integration tests the only prerequisite is to run the command : `docker-compose up`
Then we can just run the below set of commands:
`pip install -r requirements/integration.txt`
`pip install -r requirements/tests.txt`
`cd tests`
`python -m pytest -s -v`
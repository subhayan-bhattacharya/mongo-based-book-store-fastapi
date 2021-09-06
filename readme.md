# Description
A simple FastApi based rest api using mongo db as the backend

## Spinning up the service
We can use `docker-compose up` to get the service up and running


# Running tests
To run tests the below commands should suffice:
`pip install -r requirements/integration.txt`
`pip install -r requirements/tests.txt`
`cd tests`
`python -m pytest -s -v`
# Description
A simple FastApi based rest api using mongo db as the backend

## Spinning up the service
We can use `docker-compose up` to get the service up and running


## Running integration tests
The integration tests are run using `tavern`. So for it to work properly we would need to have a functional backend and have an application running
1. Bring up the service using docker-compose: `docker-compose up`
2. Go inside the `tests/integration` directory : `cd tests/integration`(This is important for integration tests!!)
3. Run the integration tests using `pytest`: `python -m pytest -s -v` 

## Running unit tests
For running the unit tests we have to do the below:
1. `cd tests/unit`
2. `pytest -s -v`
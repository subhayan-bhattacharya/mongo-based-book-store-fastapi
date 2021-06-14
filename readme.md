# Description
A simple FastApi based rest api using mongo db as the backend

## Running integration tests
The integration tests are run using tavern. So for it to work properly we would need to have a functional backend and have an application running
1. Run a docker container for the backend using the command : `docker container run -d -p 27017:27017 --name test_server mongo`
2. Connect to the docker container using `mongo` command line utility (you would need to have mongo installed) : `mongo`
3. Go to the `books` db : `use books`
4. Create the relevant indexes on the collections (The collections don't exist but have to be done anyway to make the api work): 
    1. `db.books.createIndex({name: 1}, { unique: true })`
    2. `db.authors.createIndex({name: 1}, { unique: true })`
    3. `db.genres.createIndex({name: 1}, { unique: true })`
5. Go inside the `tests/integration` directory : `cd tests/integration`(This is important for integration tests!!)
6. Run the integration tests using `pytest`: `python -m pytest -s -v`    
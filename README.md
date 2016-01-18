CSL - My Learning Plan (MLP)
===============================


Requirements
------------
- python 3
- mongodb
- sass (for flask assets)
- virtualenv and virtualenvwrapper (not a hard requirement but steps below assume you are using them)

Quickstart
----------

### Docker
Just run:
```
docker-compose up -d
```
and there should be 2 containers: web and mongo.


### Python virtual environment

Checkout this repo.

Install the requirements above if you don't already have them installed.

Then run the following commands to bootstrap your environment.

```
mkvirtualenv --python=/path/to/python3 [appname]
```
Change to the directory you checked out and install python requirements.

```
pip install -r requirements.txt
```

The base environment variables for running application locally are in environment.sh. See below for any private environment variables.

Once that this all done you can:

Start mongo:
```
mongod
```

Then run app
```
./run.sh
```
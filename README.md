CSL - My Learning Plan (MLP)
============================
This is a version of the prototype which uses [OpenLRS](http://apereo-learning-analytics-initiative.github.io/OpenLRS) as learning record store.


Service dependencies
--------------------
In order to fully run the prototype you have to have 2 other services configured and running, those are:
  - Learning Registry - [docker container](https://github.com/crossgovernmentservices/csl-learningregistry-containers)
  - Learning Records Store ([OpenLRS](https://learninglocker.net/)) - [docker container](https://github.com/crossgovernmentservices/csl-openlrs-container) 


Requirements
------------
#### Running docker
 - [Docker](https://www.docker.com)
 - [VirtualBox](https://www.virtualbox.org) - *if running on Mac*

#### Running Python virtual environment
- Python 3
- MongoDb
- SASS (for flask assets)
- virtualenv and virtualenvwrapper (not a hard requirement but steps below assume you are using them)


Quickstart
----------

### Docker
Just run:
```
docker-compose up
```
or
```
docker-compose up -d
```
and there should be 3 containers: 
  - webusers - *recreating prototype users*
  - web - *the actual running prototype*
  - mongo

You can access the prototype by navigating to your docker machine ip with port `8002`. You can find out your docker machine ip by running `docker-machine ip [machine name]` where default machine name is `default`.

### Python virtual environment


Then run the following commands to bootstrap your environment.

```
mkvirtualenv --python=/path/to/python3 [appname]
```
Change to the directory you checked out and install python requirements.

```
pip install -r requirements.txt
```

The base environment variables for running application locally are in `environment.sh`.
Once that this all done you can:

Start mongo:
```
mongod
```

Then run app
```
./run.sh
```
You can access the prototype by navigating to your localhost with port `8000`


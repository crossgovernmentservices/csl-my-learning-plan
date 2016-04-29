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


Comparison to Learning Locker
-----------------------------
A simple comparison of [Learning Locker](https://learninglocker.net) and [OpenLRS](http://apereo-learning-analytics-initiative.github.io/OpenLRS) answering the question: *how difficult would it be to switch to OpenLRS without compromising on the functionality?*

### Querying

| Learning Locker  | OpenLRS |
| ---------------- | ------- |
| **MongoDB’s Aggregation Framework**. HTTP GET with JSON passed in url params - this forces some queries values to be escaped which then may not be recognised by Mongo Aggregate API. Luckily escaped urls are mapped to their unescaped equivalent. | **Elastic Search** (mappings, dynamic mapping) - allows HTTP GET with query json in params and POST which is quite easy and has no string escaping complications. Expected async issues when querying straight after API use. |
| If it was in a distributed model **async issues would surface over here as well** | **Very simple API** - there is a simple API (looked at source code) but we haven’t explored this route |


### xApi standard

| Learning Locker  | OpenLRS |
| ---------------- | ------- |
| Keeps up with the standard. API is easy to use and user friendly. More mature behaviour, for example adds timestamp to a new statement if not present | No timestamp on OpenLRS statements (if not present on a statement LRS SHOULD fill it in using Stored value according to the specification) |
| | Given async issues one has to utilise Timestamp here - using Stored is not the best option |
| | Very close to the bone when it comes to the specification (MVP approach). Whenever the specification say SHOULD one can assume the functionality is not there. |


### Voiding statements

| Learning Locker  | OpenLRS |
| ---------------- | ------- |
| Using API with Mongo aggregation framework query to filter statements which are supposed to be voided | POST new voiding reference statement(s) which voids another (complies with the spec) |
| | Possible unnecessary void statements if going with 2 statements approach to planning - voiding Planned reference and the actual action statement |


### JSON integration

| Learning Locker  | OpenLRS |
| ---------------- | ------- |
| HTTP code: `{ code: 200 }` | HTTP code: `{ status: 200 }` |
| | Latencies (due to the distributed model) between API post and elastic search queries results on: <ul><li>**Course complete page** (new learning record - “completed”) - solved by storing info in cookie</li><li>**Plan page** after diagnostics (new plan) - can be solved in a similar fashion but it’s not for now</li><ul> | 


### Planning functionality

| Learning Locker  | OpenLRS |
| ---------------- | ------- |
| Done using SubStatement Context node | Missing Context node in Object class for SubStatements. One solution is to have 2 statements: 1 statement Planned referencing 2 statement which describes the action to complete. This creates a lot of work when it comes to statement management and filtering (especially if the planner and learner are not the same person). Aprero commented on this as not intentional and very willing to collaborate to enhance the model. |
| | For simplicity planner and learner are the same person |
| | Marking planned item as ‘done’ has not implemented as it’s a overhead for this piece of functionality to be added without Context node in SubStatement object - 2 statements workaround |


### Admin and setup

| Learning Locker  | OpenLRS |
| ---------------- | ------- |
| Long winded PHP install routine with many PHP based dependencies | Need to build the package using Maven. Good if you are familiar with this routine. Generates a “fat jar” which should be setup elsewhere |
| Comes as a complete packaged app with Admin Interface, Basic Reporting. Quite useful in general when starting to get to grips with an LRS | Once the jar or war file have been generated, the only dependency is the JVM itself, so deployment is quite simple |
| Multiple LRS and Client support within the same instance | Only supports one user per LRS instance. Each instance is a new process | 
| | No GUI, but the Apereo project has Dashboards and Other Applications that can plug-in in to create a more complete solution |

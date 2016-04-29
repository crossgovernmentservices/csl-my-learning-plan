CSL - My Learning Plan (MLP)
============================


Service dependencies
--------------------
In order to fully run the prototype you have to have 2 other services configured and running, those are:
  - Learning Registry - [docker container](https://github.com/crossgovernmentservices/csl-learningregistry-containers)
  - Learning Records Store ([Learning Locker](https://learninglocker.net/)) - [docker container](https://github.com/LearningLocker/docs/issues/15) or [installation instruction](http://docs.learninglocker.net/installation). *If you're running docker this container is included in MLP ([see docker-compose file](docker-compose.yml#L31)).*

For prototype version using [OpenLRS](http://apereo-learning-analytics-initiative.github.io/OpenLRS) instead of Learning Locker [switch to `cd-openlrs` branch](https://github.com/crossgovernmentservices/csl-my-learning-plan/tree/cd-openlrs).

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
and there should be 5 containers: 
  - webusers - *recreating prototype users*
  - web - *the actual running prototype*
  - lrs - *Learning Locker*
  - mongo
  - restore - *restoring basic Learning Locker configuration*

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


Heroku Deployment
----------
Deployment including a mongo instance can be acheived with these steps:

### Requirements
- Have the Heroku toolbelt installed.
- Cloned the GIT repository.
- Within a CLI with the current working directory set to be inside the repo.

From within the repo which will have been cloned from GIT make sure you have the Heroku toolbelt installed and supplied the credentials with `heroku login`.

### Create the application in Heroku

```
heroku apps:create csl-my-learning-plan
```

### Add MongoDB dependency
Now the application is created the MongoLab Add-On can be added. Unfortunately this can only be done from an account that is backed by a credit card, even when picking the Free Plan version of the plugin.

### Setup environment variables

Setup the environment variables for the Heroku application. These can be set via the CLI or via the Heroku App.

A MongoDB setting needs to be set. When the add-on is configured for the application a setting is automatically added. The application expects this setting to exist under another name. The value can be extracted by issuing the command 
```
heroku config -s
```

The add-on specific setting is configured under `MONGOLAB_URI`. This should be transferred over to a setting named `MONGO_URI`.

Required setting variables are:
```
SETTINGS='application.config.Config'
PYTHONPATH=fakepath
MONGO_URI='value copied from MONGOLAB_URI'
SECRET_KEY='local-dev-not-secret'
SECURITY_PASSWORD_HASH='bcrypt'
SASS_PATH='.'
LANG='en_US.UTF-8'
DGN_RULE='learning_registry_match'
LR_URL='learning registry url'
LR_QUERY_URL='/slice?any_tags=civil%20service%20learning'
LRS_HOST='learning locker url'
LRS_HTTPS_ENABLED=true
LRS_PORT=443
LRS_USER='value from learning locker'
LRS_PASS='value from learning locker'
LRS_COMMAND_API_URL=/api/v2/statements
LRS_QUERY_API_URL=/api/v1/statements
LRS_QUERY_URL='/api/v1/statements/aggregate?pipeline=%s'
LRS_STATEMENTS_URL=/data/xAPI/statements
```

*Note the `PYTHONPATH` variable is needed to work around an issue with pathing that happens when starting the application using gunicorn.*


#### Known issues
We have seen an issue where the buildpacks can get confused, resulting in the Python runtime not being setup. Check the buildpacks from command `heroku buildpacks` both Ruby and Python are needed. Ruby for sass.

Amazon Web Services based infrastructure
----------
AWS is hosting the Learner Record Store (stage.lrs.civilservice.digital, lrs.civilservice.digital) and the Learning Registry (stage.lr.civilservice.digital, lr.civilservice.digital)

If necessary, access credentials can be obtained from the GDS/CSL Team that worked on the prototype.

Once in AWS the EC2 nodes supporting the prototype are:

For the Learner Record Store (LRS):
- csl_lrs_node1, marked with tags staging and production
- *csl_lrs_mongo_node1, marked with tags staging and production

*The LRS service has gone down at one time.  This was due to MongoDB going down. A simple restart of this instance recovered the problem.

For the Learning Registry (LR): 
- csl_lr_node1, marked with tags staging and production
- csl_lr_couchdb_node1, marked with tags staging and production

The DNS entries are managed by AWS Route 53 within the civilservice.digital hosted zone.

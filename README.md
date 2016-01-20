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

Heroku Deployment
----------
Deployment including a mongo instance can be acheived with these steps:

###Requirements
- Have the Heroku toolbelt installed.
- Cloned the GIT repository.
- Within a CLI with the current working directory set to be inside the repo.

From within the repo which will have been cloned from GIT make sure you have the Heroku toolbelt installed and supplied the credentials with `heroku login`.

###Create the application in Heroku

```
heroku apps:create csl-my-learning-plan
```

###Add MongoDB dependency
Now the application is created the MongoLab Add-On can be added.  Unfortunately this can only be done from an account that is backed by a credit card, even when picking the Free Plan version of the plugin.

###Setup environment variables

Setup the environment variables for the Heroku application.  These can be set via the CLI or via the Heroku App.

A MongoDB setting needs to be set.  When the add-on is configured for the application a setting is automatically added.  The application expects this setting to exist under another name.  The value can be extracted by issuing the command 
```heroku config -s```
The add-on specific setting is configured under MONGOLAB_URI.  This should be transferred over to a setting named MONGO_URI.

Required setting variables are:

SETTINGS='application.config.Config'
PYTHONPATH=fakepath
MONGO_URI='value copied from MONGOLAB_URI'
SECRET_KEY=local-dev-not-secret
SECURITY_PASSWORD_HASH=bcrypt
SASS_PATH='.'

*Note the PYTHONPATH variable is needed to work around an issue with pathing that happens when starting the application using gunicorn.


Known issues.  We have seen an issue where the buildpacks can get confused, resulting in the Python runtime not being setup.  Check the buildpacks from command `heroku buildpacks` both Ruby and Python are needed.  Ruby for sass.






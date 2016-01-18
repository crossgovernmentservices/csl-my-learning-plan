from application.models import (
    db,
    User,
    Role
)


from flask.ext.security import MongoEngineUserDatastore
user_datastore = MongoEngineUserDatastore(db, User, Role)

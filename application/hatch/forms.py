from flask.ext.wtf import Form
from flask.ext.wtf.html5 import EmailField
from wtforms.validators import Required


class AddUserForm(Form):
    email = EmailField('Email address', validators=[Required()])

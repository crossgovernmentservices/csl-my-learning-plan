from flask.ext.wtf import Form

from flask.ext.wtf.html5 import EmailField

from wtforms.validators import Required
from wtforms.fields import (
    TextAreaField,
    HiddenField
)


class LoginForm(Form):
    email = EmailField('Email address', validators=[Required()])
    next = HiddenField('next')


class FeedbackForm(Form):
    feedback = TextAreaField('Your feedback', validators=[Required()])

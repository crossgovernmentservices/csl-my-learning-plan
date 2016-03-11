import os

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    current_app
)

from flask.ext.security import login_required
from flask.ext.security.utils import login_user

from application.mylearning.forms import LoginForm

from application.models import User

from application.extensions import user_datastore


mylearning = Blueprint('mylearning', __name__, template_folder='templates')


@mylearning.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@mylearning.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.args.get('next'):
        form.next.data = request.args.get('next')
    if form.validate_on_submit():
        current_app.logger.info(form.data)
        email = form.email.data.strip()
        user = user_datastore.get_user(email)
        if not user:
            flash("You don't have a user account yet")
            return redirect(url_for('mylearning.index'))
        login_user(user)

        # TODO check next is valid
        return redirect(form.next.data)
    return render_template('login.html', form=form)


@mylearning.route('/users.json')
@login_required
def users():
    email = request.args.get('email', '')
    users = User.objects.filter(email__contains=email)
    return jsonify({'users': users})

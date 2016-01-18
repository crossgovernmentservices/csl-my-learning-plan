from flask import (
    Blueprint,
    render_template,
    url_for,
    redirect,
    flash,
    request
)

from flask.ext.security.decorators import roles_required
from flask.ext.security.utils import encrypt_password

# from flask.ext.login import current_user

from application.models import User

hatch = Blueprint('hatch', __name__, url_prefix='/the-hatch')


@hatch.route("/")
@roles_required('ADMIN')
def open():
    return render_template('hatch/hatch.html')


@hatch.route("/manage-users")
@roles_required('ADMIN')
def manage_users():
    users = User.objects
    return render_template('hatch/manage_users.html', users=users)


@hatch.route("/add-user", methods=['POST'])
@roles_required('ADMIN')
def add_user():
    from application.extensions import user_datastore
    email = request.form['email']
    full_name = request.form['full-name']
    if not User.objects.filter(email=email).first():
        password = encrypt_password('password')
        user = user_datastore.create_user(email=email,
                                          password=password,
                                          full_name=full_name)
        user_role = user_datastore.find_or_create_role('USER')
        user_datastore.add_role_to_user(user, user_role)
        user.save()

    flash("Saved user " + email)
    return redirect(url_for('hatch.open'))


# @hatch.route("/add-objective", methods=['POST'])
# @roles_required('ADMIN')
# def add_objective():
#     what = request.form['what']
#     how = request.form['how']
#     objective = Objective(what=what, how=how)
#     current_user.objectives.add(objective)
#     return 'Created objective for ' + current_user.email


# @hatch.route("/delete-objectives/<email>")
# @roles_required('ADMIN')
# def delete_objectives(email):
#     user = User.objects.filter(email=email).first()
#     user.objectives.objectives = []
#     user.objectives.save()
#     return redirect(url_for('hatch.manage_users'))

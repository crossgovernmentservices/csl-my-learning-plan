from flask import (
    Blueprint,
    render_template,
    redirect,
    flash,
    url_for,
    request
)

from flask.ext.security import login_required
from flask.ext.login import current_user

from application.profile.forms import EmailForm, UpdateDetailsForm


profile = Blueprint('profile', __name__, template_folder='templates')


@profile.route('/profile')
@login_required
def view_profile():
    return render_template('profile/profile.html')


@profile.route('/profile/add-email', methods=['GET', 'POST'])
@login_required
def add_email():
    form = EmailForm()
    user = current_user
    if form.validate_on_submit():
        email = form.email.data.strip()
        if email not in user.other_email and email != user.email:
            user.other_email.append(email)
            user.save()
            message = "Sucessfully added email %s" % email
        else:
            message = "Already have email: %s" % email
        flash(message)
        return redirect(url_for('profile.view_profile'))
    else:
        return render_template('profile/add-email.html', form=form)


@profile.route('/profile/remove-email')
@login_required
def remove_email():
    email = request.args.get('email')
    user = current_user
    if email:
        email = email.strip()
        user.other_email.remove(email)
        user.save()
        message = "Removed email: %s" % email
        flash(message)
    return redirect(url_for('profile.view_profile'))


def update_details_form():
    form = UpdateDetailsForm()
    return form


@profile.route('/profile/update-details', methods=['GET', 'POST'])
@login_required
def update_details():
    form = update_details_form()
    user = current_user
    if form.validate_on_submit():
        if form.grade.data:
            user.grade = form.grade.data.strip()
        if form.profession.data:
            user.profession = form.profession.data.strip()
        if form.grade.data or form.profession.data:
            user.save()
            message = "Successfully updated details"
        else:
            message = "No new details submitted"
        flash(message)
        return redirect(url_for('profile.view_profile'))
    else:
        return render_template('profile/update-details.html', form=form)

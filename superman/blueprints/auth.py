# -*- coding: utf-8 -*-
# Author: zhuima


from flask_babel import lazy_gettext as _
from flask import request, render_template, flash, redirect, url_for, Blueprint, g, current_app, make_response, jsonify
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required
from superman.forms import LoginForm, RegistrationForm, ChangePasswordForm
from superman.utils import redirect_back
from superman.models import Admin, HostGroup, HostInfo
from superman.extensions import db


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        if form.validate_on_submit():
            user = Admin.query.filter_by(username=form.username.data.lower()).first()
            if user is not None and user.validate_password(form.password.data):
                if login_user(user, form.remember.data):
                    flash(_('Login success.'), 'success')
                    # flash(message=_('Login success.', 'info'))
                    return redirect_back()
                else:
                    flash(_('Your account is blocked.'), 'warning')
                    return redirect(url_for('auth.login'))
            flash(_('Invalid username or password.'), 'warning')
    return render_template('login.html', form=form)



@auth_bp.route('/user/', methods=['GET', 'POST'])
@login_required
def user():
    return render_template('page-user.html')


@auth_bp.route('/userlist', methods=['GET', 'POST'])
@fresh_login_required
@login_required
def userlist():
	# return render_template('info.html')
    page = request.args.get('page', 1, type=int)
    pagination = Admin.query.order_by(Admin.id.desc()).paginate(
        page, per_page=current_app.config['SUPERMAN_MANAGE_POST_PER_PAGE'])
    users = pagination.items
    return render_template('users.html', page=page, pagination=pagination, users=users)


@auth_bp.route('/userlist/new', methods=['GET', 'POST'])
@fresh_login_required
@login_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        admin = Admin(username=form.username.data)
        password = form.password.data
        # print(password)
        admin.set_password(password)
        # add employee to the database
        db.session.add(admin)
        db.session.commit()
        flash(_('You have successfully registered! You can try login.'), 'success')
        # redirect to the login page
        return redirect(url_for('auth.userlist'))

    # load registration template
    return render_template('new_user.html', form=form)



@auth_bp.route('/userlist/<int:user_id>/delete', methods=['GET', 'DELETE'])
@fresh_login_required
@login_required
def delete_user(user_id):
    admin = Admin.query.get_or_404(user_id)
    db.session.delete(admin)
    db.session.commit()
    flash(_('User delete.'), 'success')
    # return redirect(url_for('dashboard.userlist'))
    return jsonify({'ret': 'success'})



@auth_bp.route('/userlist/<int:user_id>/change-password', methods=['GET', 'POST'])
@fresh_login_required
@login_required
def change_password(user_id):
    user = Admin.query.get_or_404(user_id)
    form = ChangePasswordForm()
    if form.validate_on_submit() and user.validate_password(form.old_password.data):
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Password updated.'), 'success')
        return redirect(url_for('auth.userlist', username=user.username))
    return render_template('change_password.html', form=form, username=user.username)


@auth_bp.route('/set-locale/<locale>')
@login_required
def set_locale(locale):
    if current_user.is_authenticated:
        current_user.locale = locale
        db.session.commit()
    else:
        response.set_cookie('locale', locale, max_age=60 * 60 * 24 * 30)
    flash(_('Setting locale %(locale)s updated.', locale=locale), 'success')
    return redirect(url_for('dashboard.dashboard'))


@auth_bp.route('/logout')
@fresh_login_required
@login_required
def logout():
    logout_user()
    flash(_('Logout success.'), 'success')
    return redirect(url_for('auth.login'))

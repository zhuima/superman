# -*- coding: utf-8 -*-
# Author: zhuima


from flask_babel import lazy_gettext as _
from wtforms.widgets.core import PasswordInput
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, BooleanField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional, URL, EqualTo, Regexp, IPAddress, NumberRange
from superman.models import Admin, HostGroup, HostInfo


class MyPasswordField(PasswordField):
    '''
    custom password field to display
    '''
    widget = PasswordInput(hide_value=False)


class LoginForm(FlaskForm):
    username = StringField(_('Username'), validators=[DataRequired(), Length(3, 20)])
    password = PasswordField(_('Password'), validators=[DataRequired(), Length(6, 128)])
    remember = BooleanField(_('Remember me'))
    submit = SubmitField(_('Log in'))


    def validate_name(self, field):
        if Admin.query.filter_by(name=field.data).first():
            raise ValidationError('Name {0} is already in use.'.format(field.data))


class RegistrationForm(FlaskForm):
    """
    Form for users to create new account
    """
    username = StringField(_('Username'), validators=[DataRequired(), Length(3, 20)])

    password = PasswordField(_('Password'), validators=[
                                        DataRequired(),
                                        Length(6, 128),
                                        EqualTo('confirm_password')
                                        ])
    confirm_password = PasswordField(_('Confirm Password'), validators=[DataRequired()])
    submit = SubmitField(_('New User'))


    def validate_username(self, field):
        if Admin.query.filter_by(username=field.data).first():
            raise ValidationError('Username {0} is already in use.'.format(field.data))


class ResetPasswordForm(FlaskForm):
    username = StringField(_('Username'), validators=[DataRequired(), Length(1, 20)])

    password = PasswordField(_('Password'), validators=[
        DataRequired(), Length(6, 128), EqualTo('confirm_password')])
    confirm_password = PasswordField(_('Confirm Password'), validators=[DataRequired()])
    submit = SubmitField(_('Rest Password'))


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(_('Old Password'), validators=[DataRequired()])
    password = PasswordField(_('New Password'), validators=[
        DataRequired(), Length(6, 128), EqualTo('confirm_password')])
    confirm_password = PasswordField(_('Confirm Password'), validators=[DataRequired()])
    submit = SubmitField(_('Rest Password'))


class HostGroupForm(FlaskForm):
    name = StringField(_('Name'), validators=[DataRequired(), Length(1, 30)])
    comment = TextAreaField(_('Comment'), validators=[DataRequired(), Length(1, 254)])
    submit = SubmitField(_('Add HostGroup'))


    def validate_name(self, field):
        if HostGroup.query.filter_by(name=field.data).first():
            raise ValidationError('Name {0} is already in use.'.format(field.data))


class EditHostGroupForm(FlaskForm):
    name = StringField(_('Name'), validators=[DataRequired(), Length(1, 30)])
    comment = TextAreaField(_('Comment'), validators=[DataRequired(), Length(1, 254)])
    submit = SubmitField(_('Update HostGroup'))

    def __init__(self, hostgroup, *args, **kwargs):
        super(EditHostGroupForm, self).__init__(*args, **kwargs)
        self.hostgroup = hostgroup

    def validate_name(self, field):
        if field.data != self.hostgroup.name and HostGroup.query.filter_by(name=field.data).first():
            raise ValidationError('Name {0} is already in use.'.format(field.data))


class HostInfoForm(FlaskForm):
    host = StringField(_('Hosts Num'), validators=[DataRequired(), IPAddress(), Length(1, 128)])
    port = IntegerField('Port', validators=[NumberRange(min=2, max=10086)])
    username = StringField(_('Username'), validators=[DataRequired(), Length(1, 128)])
    password = MyPasswordField(_('Password'), validators=[DataRequired(), Length(1, 128)])
    hostgroup = SelectField(_('HostGroup'), coerce=int, default=1)
    comment = TextAreaField(_('Comment'), validators=[Length(1, 254)])
    submit = SubmitField(_('Add Host'))

    def validate_host(self, field):
        if HostInfo.query.filter_by(host=field.data).first():
            raise ValidationError('Host {0} is already in use.'.format(field.data))


    def __init__(self, *args, **kwargs):
        super(HostInfoForm, self).__init__(*args, **kwargs)
        self.hostgroup.choices = [(hostgroup.id, hostgroup.name)
                                 for hostgroup in HostGroup.query.order_by(HostGroup.name).all()]



class EditHostInfoForm(FlaskForm):
    host = StringField(_('Hosts Num'), validators=[DataRequired(), IPAddress(), Length(1, 128)])
    port = IntegerField('Port', validators=[NumberRange(min=2, max=10086)])

    username = StringField(_('Username'), validators=[DataRequired(), Length(1, 128)])
    password = MyPasswordField(_('Password'), validators=[DataRequired(), Length(1, 128)])
    hostgroup = SelectField(_('HostGroup'), coerce=int)
    comment = TextAreaField(_('Comment'), validators=[Length(1, 254)])
    submit = SubmitField(_('Update Host'))


    def __init__(self, hostinfo, *args, **kwargs):
        super(EditHostInfoForm, self).__init__(*args, **kwargs)
        self.hostgroup.choices = [(hostgroup.id, hostgroup.name)
                                 for hostgroup in HostGroup.query.order_by(HostGroup.name).all()]

        self.hostinfo = hostinfo


    def validate_host(self, field):
        if field.data != self.hostinfo.host and HostInfo.query.filter_by(host=field.data).first():
            raise ValidationError('Host {0} is already in use.'.format(field.data))
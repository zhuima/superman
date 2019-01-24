from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from superman.extensions import db, whooshee


@whooshee.register_model('username')
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True)
    password_hash = db.Column(db.String(128))
    locale = db.Column(db.String(20))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


@whooshee.register_model('name')
class HostGroup(db.Model):
    __tablename__ = 'hostgroup'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)

    hostinfos = db.relationship('HostInfo', back_populates='hostgroup')

    def __repr__(self):
        return '<HostGroup %r>' % self.name



@whooshee.register_model('host')
class HostInfo(db.Model):
    __tablename__ = 'hostinfo'

    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(64), unique=True, index=True)
    port = db.Column(db.Integer)
    username = db.Column(db.String(64))
    password = db.Column(db.String(128))
    comment= db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)

    group_id = db.Column(db.Integer, db.ForeignKey('hostgroup.id'))
    hostgroup = db.relationship('HostGroup', back_populates='hostinfos')

    def __repr__(self):
        return '<HostInfo %r>' % self.host

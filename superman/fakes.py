# -*- coding: utf-8 -*-
# Author: zhuima


from faker import Faker

from superman.models import Admin
from superman.extensions import db


fake = Faker()

def fake_admin():
    admin = Admin(
        username='admin',
    )
    admin.set_password('zhuima321')
    db.session.add(admin)
    db.session.commit()

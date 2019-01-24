from flask import request, current_app
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from flask_whooshee import Whooshee
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_migrate import Migrate



bootstrap = Bootstrap()
moment = Moment()
babel = Babel()
whooshee = Whooshee()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()



login_manager.login_view = 'auth.login'
login_manager.login_message = _l('Please login to access this page.')

login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    from superman.models import Admin
    user = Admin.query.get(int(user_id))
    return user

@babel.localeselector
def get_locale():
    if current_user.is_authenticated and current_user.locale is not None:
        return current_user.locale

    locale = request.cookies.get('locale')
    if locale is not None:
        return locale
    return request.accept_languages.best_match(current_app.config['SUPERMAN_LOCALES'])


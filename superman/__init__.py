# -*- coding: utf-8 -*-
# Author: zhuima



import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import click
from flask import Flask, render_template
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError


from superman.blueprints.dashboard import dashboard_bp
from superman.blueprints.admin import admin_bp
from superman.blueprints.auth import auth_bp
from superman.settings import config


from superman.extensions import bootstrap, moment, babel, whooshee, db, login_manager, csrf, migrate
from superman.models import Admin, HostGroup, HostInfo
from superman.settings import config



basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('superman')
    app.config.from_object(config[config_name])

    register_logging(app)
    register_shell_context(app)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errors(app)
    return app


def register_logging(app):
    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/superman.log'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)


    if not app.debug:
        app.logger.addHandler(file_handler)



def register_extensions(app):
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    whooshee.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Admin=Admin, HostGroup=HostGroup, HostInfo=HostInfo)




def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # @app.errorhandler(CSRFError)
    # def handle_csrf_error(e):
    #     return render_template('errors/400.html', description=e.description), 400




def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')


    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    @click.argument('locale')
    def init(locale):
        """Initialize a new language."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system(
                'pybabel init -i messages.pot -d superman/translations -l ' + locale):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')

    @translate.command()
    def update():
        """Update all languages."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d superman/translations'):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system('pybabel compile -d superman/translations'):
            raise RuntimeError('compile command failed')
            

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        """Building Bluelog, just for you."""

        click.echo('Initializing the database...')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username
            )
            admin.set_password(password)
            db.session.add(admin)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    def forge():
        """Generate fake data."""
        from superman.fakes import fake_admin

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        
        click.echo('Done.')


def register_request_handlers(app):
    @app.after_request
    def query_profiler(response):
        for q in get_debug_queries():
            if q.duration >= app.config['SUPERMAN_SLOW_QUERY_THRESHOLD']:
                app.logger.warning(
                    'Slow query: Duration: %fs\n Context: %s\nQuery: %s\n '
                    % (q.duration, q.context, q.statement)
                )
        return response
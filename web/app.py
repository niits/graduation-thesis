import os

from blueprints import admin, auth, data, main, plot, landing_page
from celery import Celery
from database import PredictEnum, User, db, migrate
from flask import Flask
from flask_login import LoginManager

config_variable_name = "FLASK_CONFIG_PATH"
default_config_path = os.path.join(os.path.dirname(__file__), "config/local.py")
os.environ.setdefault(config_variable_name, default_config_path)


def create_app(config_file=None, settings_override=None):
    app = Flask(__name__)
    app.secret_key = "super secret key"
    @app.after_request
    def after_request(response):
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        header['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE, PUT'
        return response
    if config_file:
        app.config.from_pyfile(config_file)
    else:
        app.config.from_envvar(config_variable_name)

    if settings_override:
        app.config.update(settings_override)

    init_app(app)

    return app


def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(main.bp)
    app.register_blueprint(plot.bp)
    app.register_blueprint(data.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(landing_page.bp)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    @app.template_filter("convert_enum")
    def convert_enum(value):
        return (
            "Là bot"
            if value == PredictEnum.bot
            else (
                "Không là bot"
                if value == PredictEnum.not_bot
                else "Chưa được đoán nhận"
            )
        )

    @app.template_filter("convert_boolean")
    def convert_boolean(value):
        return "Có" if value else "Không"


def create_celery_app(app=None):
    app = app or create_app()
    celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
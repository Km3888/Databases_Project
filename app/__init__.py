from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from config import config
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.auth'  #route for auth page prefixed with auth blueprint name


bootstrap = Bootstrap()
db = SQLAlchemy()
moment=Moment()

from .models import BookingAgent

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .public import public as public_blueprint
    app.register_blueprint(public_blueprint,url_prefix='/public')

    from .customer import customer as customer_blueprint
    app.register_blueprint(customer_blueprint,url_prefix='/customer')

    from .agent import agent as agent_blueprint
    app.register_blueprint(agent_blueprint, url_prefix='/agent')

    from .staff import staff as staff_blueprint
    app.register_blueprint(staff_blueprint,url_prefix='/staff')
    # from .booking import booking as booking_blueprint
    # app.register_blueprint(booking_blueprint,url_prefix='/booking')
    return app
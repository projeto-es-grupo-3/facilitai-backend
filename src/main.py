from flask_cors import CORS
from flask import Flask 
from werkzeug.security import gen_salt

from datetime import timedelta

from .model import db
from .routes import bp, init_jwt

def create_app():
    app = Flask(__name__)

    CORS(app)

    # app configurations
    setup_app(app)

    return app


def setup_app(app):

    # configure secret key
    app.config['SECRET_KEY'] = gen_salt(48)

    # register main blueprint
    app.register_blueprint(bp)

    # initialize JWTManager
    init_jwt(app)

    # database uri
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///facilitai'

    # jwt configuration
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_SECRET_KEY'] = gen_salt(48)

    # initialize database
    @app.before_first_request
    def create_tables():
        db.create_all()

    db.init_app(app)

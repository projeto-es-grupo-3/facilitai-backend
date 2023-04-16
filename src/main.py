from flask_cors import CORS
from flask import Flask, Blueprint

def create_app(config_filename):
    app = Flask(__name__)
    CORS(app)

    # app configurations
    setup_app(app)

    return app


def setup_app(app):

    # register main blueprint
    bp = Blueprint('bp', __name__, template_folder='templates', url_prefix='')
    app.register_blueprint(bp)

    # from model import db
    # db.init_app(app)

    # from yourapplication.views.admin import admin
    # from yourapplication.views.frontend import frontend
    # app.register_blueprint(admin)
    # app.register_blueprint(frontend)

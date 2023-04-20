from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from .model import (
    User,
    db
)

bp = Blueprint('bp', __name__, template_folder='templates', url_prefix='')

def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


@bp.route('/register', methods=['POST'])
def register():
    username = request.json["username"]
    email = request.json["email"]
    matricula = request.json["matricula"]
    campus = request.json["campus"]
    password = request.json["password"]
    curso = request.json["curso"]

    new_user = User(username, email, matricula, campus, generate_password_hash(password), curso)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(message='User created.'), 200


@bp.route('/login', methods=['POST'])
def login():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.pass_hash, password):
        session['id'] = user.id
        return jsonify("Successfully logged in."), 200
    
    return jsonify("Invalid credentials"), 401

@bp.route('/logout')
def logout():
    del session['id']
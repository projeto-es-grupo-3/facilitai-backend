from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(30), unique=True, nullable=False)

    email = db.Column(db.String, unique=True, nullable=False)


class Anuncio(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    
    titulo = db.Column(db.String(70), unique=True, nullable=False)
    
    anunciante = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    preco = db.Column(db.Float, nullable=False)


class Livro(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    
    titulo = db.Column(db.String(20), unique=True, nullable=False)
    
    autor = db.Column(db.String(20), unique=True, nullable=True)

    genero = db.Column(db.String(20), unique=True, nullable=True)


class Apartamento(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    
    endereco = db.Column(db.String(70), unique=True, nullable=False)
    
    area = db.Column(db.Integer, nullable=True)
    
    comodos = db.Column(db.Integer, nullable=True)

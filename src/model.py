from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(30), unique=True, nullable=False)

    matricula = db.Column(db.String, unique=True, nullable=False)

    pass_hash = db.Column(db.String, nullable=False)

    email = db.Column(db.String, unique=True, nullable=False)
    
    campus = db.Column(db.String, nullable=False)

    curso = db.Column(db.String, nullable=False)

    def __init__(self, username, email, matricula, campus, pass_hash, curso):
        self.username = username
        self.matricula = matricula
        self.campus = campus
        self.email = email
        self.pass_hash = pass_hash
        self.curso = curso


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

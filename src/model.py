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
    
    titulo = db.Column(db.String(70), unique=False, nullable=False)
    
    anunciante = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    descricao = db.Column(db.String(500), unique=False, nullable=False)
    
    preco = db.Column(db.Float, nullable=False)


class AnuncioLivro(Anuncio, db.Model):

    id = db.Column(db.Integer, db.ForeignKey('anuncio.id'), primary_key=True)

    titulo_livro = db.Column(db.String(20), unique=True, nullable=False)
    
    autor = db.Column(db.String(20), unique=True, nullable=True)

    genero = db.Column(db.String(20), unique=True, nullable=True)

    anuncio = db.relationship(Anuncio, backref='anuncio_livro')
    
    def __init__(self, titulo, anunciante, descricao, preco, titulo_livro, autor, genero):
        super.titulo = titulo
        super.anunciante = anunciante
        super.descricao = descricao
        super.preco = preco
        self.titulo_livro = titulo_livro
        self.autor = autor
        self.genero = genero


class AnuncioApartamento(Anuncio, db.Model):

    id = db.Column(db.Integer, db.ForeignKey('anuncio.id'), primary_key=True)
    
    endereco = db.Column(db.String(70), unique=True, nullable=False)
    
    area = db.Column(db.Integer, nullable=True)
    
    comodos = db.Column(db.Integer, nullable=True)

    anuncio = db.relationship(Anuncio, backref='anuncio_apartamento')

    def __init__(self, titulo, anunciante, descricao, preco, endereco, area, comodos):
        super.titulo = titulo
        super.anunciante = anunciante
        super.descricao = descricao
        super.preco = preco
        self.endereco = endereco
        self.area = area
        self.comodos = comodos

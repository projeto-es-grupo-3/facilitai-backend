from flask_sqlalchemy import SQLAlchemy
from enum import Enum

from conf.config import IMAGE


db = SQLAlchemy()

class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(30), unique=True, nullable=False)

    matricula = db.Column(db.String, unique=True, nullable=False)

    pass_hash = db.Column(db.String, nullable=False)

    email = db.Column(db.String, unique=True, nullable=False)
    
    campus = db.Column(db.String, nullable=False)

    curso = db.Column(db.String, nullable=False)

    rating = db.Column(db.Integer, nullable=True)

    anuncios = db.relationship('Anuncio', back_populates='anunciante')

    anuncios_favoritos = db.relationship('Anuncio', secondary='favorites')

    profile_img = db.Column(db.String)

    def to_dict(self):
        return {
            'username': self.username,
            'matricula': self.matricula,
            'email': self.email,
            'campus': self.campus,
            'curso': self.curso
        }

    def __init__(self, username, email, matricula, campus, pass_hash, curso):
        self.username = username
        self.matricula = matricula
        self.campus = campus
        self.email = email
        self.pass_hash = pass_hash
        self.curso = curso


class StatusAnuncio(Enum):
    AGUARDANDO_ACAO = 'Aguardando Ação'
    TROCADO = 'Trocado'
    VENDIDO = 'Vendido'
    DOADO = 'Doado'


class Anuncio(db.Model):

    __tablename__ = 'anuncio'

    id = db.Column(db.Integer, primary_key=True)
    
    titulo = db.Column(db.String(70), unique=False, nullable=False)
    
    anunciante = db.relationship('User', back_populates='anuncios')

    descricao = db.Column(db.String(500), unique=False, nullable=False)
    
    preco = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(20), default=StatusAnuncio.AGUARDANDO_ACAO.name, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    ad_img = db.Column(db.String)

    # coluna que serve como diferenciador de tipo na tabela para representar os tipos
    type_discriminator :  db.Mapped[str]

    __mapper_args__ = {
        'polymorphic_on': 'type_discriminator',
        'polymorphic_identity': 'anuncio'
    }

    def __init__(self, titulo, anunciante, descricao, preco, status=StatusAnuncio.AGUARDANDO_ACAO):
        self.titulo = titulo
        self.anunciante = anunciante
        self.descricao = descricao
        self.preco = preco
        self.status = status.name

    def is_from_user(self, user):
        if self.anunciante == user: return True

        return False


class AnuncioLivro(Anuncio, db.Model):

    id = db.Column(db.Integer, db.ForeignKey('anuncio.id'), primary_key=True)

    titulo_livro = db.Column(db.String(20), unique=False, nullable=False)
    
    autor = db.Column(db.String(20), unique=False, nullable=True)

    genero = db.Column(db.String(20), unique=False, nullable=True)

    aceita_trocas = db.Column(db.Boolean, default=False, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity':'anuncio_livro',
    }

    def to_dict(self):
        return {
            'titulo': self.titulo,
            'anunciante': self.anunciante.to_dict(),
            'descricao': self.descricao,
            'preco': self.preco,
            'titulo_livro': self.titulo_livro,
            'autor': self.autor,
            'genero': self.genero,
            'status': self.status,
            'aceita_trocas': self.aceita_trocas,
            'image_location': f'{IMAGE.removesuffix("<file_name>")}{self.ad_img}'
        }

    def get_to_dict(self):
        return {
            'titulo': self.titulo,
            'anunciante': self.anunciante.username,
            'descricao': self.descricao,
            'preco': self.preco,
            'titulo_livro': self.titulo_livro,
            'autor': self.autor,
            'genero': self.genero,
            'status': self.status,
            'aceita_trocas': self.aceita_trocas,
            'image_location': f'{IMAGE.removesuffix("<file_name>")}{self.ad_img}'
        }

    def __init__(self, titulo, anunciante, descricao, preco, status, titulo_livro, autor, genero, aceita_trocas=False):
        super().__init__(titulo, anunciante, descricao, preco, status)
        self.titulo_livro = titulo_livro
        self.autor = autor
        self.genero = genero
        self.aceita_trocas = aceita_trocas


class AnuncioApartamento(Anuncio, db.Model):

    id = db.Column(db.Integer, db.ForeignKey('anuncio.id'), primary_key=True)
    
    endereco = db.Column(db.String(70), unique=True, nullable=False)
    
    area = db.Column(db.Integer, nullable=True)
    
    comodos = db.Column(db.Integer, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity':'anuncio_apartamento',
    }

    def to_dict(self):
        return {
            'titulo': self.titulo,
            'anunciante': self.anunciante.to_dict(),
            'descricao': self.descricao,
            'preco': self.preco,
            'endereco': self.endereco,
            'area': self.area,
            'comodos': self.comodos,
            'status': self.status,
            'image_location': f'{IMAGE.removesuffix("<file_name>")}{self.ad_img}'
        }

    def get_to_dict(self):
        return {
            'titulo': self.titulo,
            'anunciante': self.anunciante.username,
            'descricao': self.descricao,
            'preco': self.preco,
            'endereco': self.endereco,
            'area': self.area,
            'comodos': self.comodos,
            'status': self.status,
            'image_location': f'{IMAGE.removesuffix("<file_name>")}{self.ad_img}'
        }

    def __init__(self, titulo, anunciante, descricao, preco, status, endereco, area, comodos):
        super().__init__(titulo, anunciante, descricao, preco, status)
        self.endereco = endereco
        self.area = area
        self.comodos = comodos


class TokenBlockList(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    jti = db.Column(db.String(36), nullable=False, index=True)

    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, jti, created_at):
        self.jti = jti
        self.created_at = created_at


class Favorites(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    anuncio_id = db.Column(db.Integer, db.ForeignKey('anuncio.id'), nullable=False)

    def __init__(self, user_id, anuncio_id):
        self.user_id = user_id
        self.anuncio_id = anuncio_id

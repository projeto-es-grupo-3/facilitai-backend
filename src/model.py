from flask_sqlalchemy import SQLAlchemy


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

    anuncios = db.relationship('Anuncio', back_populates='anunciante')

    def __init__(self, username, email, matricula, campus, pass_hash, curso):
        self.username = username
        self.matricula = matricula
        self.campus = campus
        self.email = email
        self.pass_hash = pass_hash
        self.curso = curso


class Anuncio(db.Model):

    __tablename__ = 'anuncio'

    id = db.Column(db.Integer, primary_key=True)
    
    titulo = db.Column(db.String(70), unique=False, nullable=False)
    
    anunciante = db.relationship('User', back_populates='anuncios')

    descricao = db.Column(db.String(500), unique=False, nullable=False)
    
    preco = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # coluna que serve como diferenciador de tipo na tabela para representar os tipos
    type_discriminator :  db.Mapped[str]

    __mapper_args__ = {
        'polymorphic_on': 'type_discriminator',
        'polymorphic_identity': 'anuncio'
    }

    def __init__(self, titulo, anunciante, descricao, preco):
        self.titulo = titulo
        self.anunciante = anunciante
        self.descricao = descricao
        self.preco = preco


class AnuncioLivro(Anuncio, db.Model):

    id = db.Column(db.Integer, db.ForeignKey('anuncio.id'), primary_key=True)

    titulo_livro = db.Column(db.String(20), unique=False, nullable=False)
    
    autor = db.Column(db.String(20), unique=False, nullable=True)

    genero = db.Column(db.String(20), unique=False, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity':'anuncio_livro',
    }

    def __init__(self, titulo, anunciante, descricao, preco, titulo_livro, autor, genero):
        super().__init__(titulo, anunciante, descricao, preco)
        self.titulo_livro = titulo_livro
        self.autor = autor
        self.genero = genero


class AnuncioApartamento(Anuncio, db.Model):

    id = db.Column(db.Integer, db.ForeignKey('anuncio.id'), primary_key=True)
    
    endereco = db.Column(db.String(70), unique=True, nullable=False)
    
    area = db.Column(db.Integer, nullable=True)
    
    comodos = db.Column(db.Integer, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity':'anuncio_apartamento',
    }

    def __init__(self, titulo, anunciante, descricao, preco, endereco, area, comodos):
        super().__init__(titulo, anunciante, descricao, preco)
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
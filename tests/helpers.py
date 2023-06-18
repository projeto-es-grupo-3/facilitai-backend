from werkzeug.security import generate_password_hash

from models.model import User, AnuncioLivro, AnuncioApartamento, StatusAnuncio
from conf.config import LOGIN


class Helpers:
    @staticmethod
    def create_user(db_session, faker):
        password = '12345678'
        password_hash = generate_password_hash(password)
        email = faker.email()

        new_user = User(
            'user.name',
            email,
            '120120120',
            'CG',
            password_hash,
            'CC'
        )

        db_session.add(new_user)
        db_session.commit()

        return new_user, password


    @staticmethod
    def create_book_ad(db_session, constructor):
        anuncio = AnuncioLivro(constructor['titulo'], constructor['anunciante'], 
                               constructor['descricao'], constructor['preco'], 
                               StatusAnuncio.AGUARDANDO_ACAO, constructor['titulo_livro'], 
                               constructor['autor'], constructor['genero'], 
                               constructor['aceita_trocas']) 

        db_session.add(anuncio)
        db_session.commit()
        return anuncio


    @staticmethod
    def create_ap_ad(db_session, constructor):
        anuncio = AnuncioApartamento(constructor['titulo'], constructor['anunciante'], 
                                     constructor['descricao'], constructor['preco'], 
                                     StatusAnuncio.AGUARDANDO_ACAO, constructor['endereco'], 
                                     constructor['area'], constructor['comodos'])

        db_session.add(anuncio)
        db_session.commit()
        return anuncio


    @staticmethod
    def bearer_header(token):
        return {'Authorization': f"Bearer {token}"}

    @staticmethod
    def login_user(user, password, client, json_headers):
        body = {
            "username": user.username,
            "password": password
        }

        login = client.post(LOGIN, headers=json_headers, json=body)
        login_json = login.json

        access_token = login_json['access_token']

        return access_token
from werkzeug.security import generate_password_hash

from models.model import User, AnuncioLivro, AnuncioApartamento


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
                               constructor['status'], constructor['titulo_livro'], 
                               constructor['autor'], constructor['genero'], 
                               constructor['aceita_trocas']) 

        db_session.add(anuncio)
        db_session.commit()
        return anuncio


    @staticmethod
    def create_ap_ad(db_session, constructor):
        anuncio = AnuncioApartamento(constructor['titulo'], constructor['anunciante'], 
                                     constructor['descricao'], constructor['preco'], 
                                     constructor['status'], constructor['endereco'], 
                                     constructor['area'], constructor['comodos'])

        db_session.add(anuncio)
        db_session.commit()
        return anuncio


    @staticmethod
    def bearer_header(token):
        return {'Authorization': f"Bearer {token}"}
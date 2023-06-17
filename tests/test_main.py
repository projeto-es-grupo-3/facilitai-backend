from src.models.model import User, AnuncioLivro, AnuncioApartamento, StatusAnuncio
from src.conf.config import (
    REGISTER,
    LOGIN,
    LOGOUT,
    CREATE_AD,
    UPDATE,
    DELETE_AD,
    GET_FAV_ADS,
    SEARCH_BOOKS,
    SEARCH_APARTMENTS
)


def test_user_register_success(client, db_session, json_headers):
    body = {
        "username": "test-user-name",
        "email": "test.email@gmai.com",
        "matricula": "110110110",
        "campus": "SEDE",
        "password": "123456",
        "curso": "CC"
    }

    response = client.post(REGISTER, headers=json_headers, json=body)

    assert response.status_code == 201

    user = db_session.query(User).first()
    assert user.email == body['email']
    assert user.username == body['username']


def test_user_register_fail_fields(client, json_headers):
    body = {
        "username": "test-user-name",
        "email": "test.email@gmai.com",
        "matricula": "110110110",
        "campus": None,
        "password": "123456",
        "curso": "CC"
    }

    # test all fields requirement
    response = client.post(REGISTER, headers=json_headers, json=body)

    error_msg = 'Todos os campos precisam ser preenchidos.'
    assert response.status_code == 400
    assert error_msg in response.text


def test_user_register_fail_matricula(client, json_headers):
    body = {
        "username": "test-user-name",
        "email": "test.email@gmai.com",
        "matricula": "110110",
        "campus": "SEDE",
        "password": "123456",
        "curso": "CC"
    }

    # test valid matricula
    response = client.post(REGISTER, headers=json_headers, json=body)

    error_msg = 'Matricula Inválida'
    assert response.status_code == 400
    assert error_msg in response.text


def test_user_register_fail_user_already_exists(client, json_headers, helpers, db_session, faker):
    user = helpers.create_user(db_session, faker)[0]
    body = {
        "username": user.username,
        "email": "test.email@gmai.com",
        "matricula": "110110110",
        "campus": "SEDE",
        "password": "123456",
        "curso": "CC"
    }

    response = client.post(REGISTER, headers=json_headers, json=body)

    error_msg = 'Esse usuario já está cadastrado no sistema.'
    assert response.status_code == 409
    assert error_msg in response.text


def test_user_register_fail_email_already_exists(client, json_headers, helpers, db_session, faker):
    user = helpers.create_user(db_session, faker)[0]
    body = {
        "username": "test-user-name",
        "email": user.email,
        "matricula": "110110110",
        "campus": "SEDE",
        "password": "123456",
        "curso": "CC"
    }

    response = client.post(REGISTER, headers=json_headers, json=body)

    error_msg = 'Esse e-mail já está cadastrado no sistema.'
    assert response.status_code == 409
    assert error_msg in response.text


def test_user_register_fail_matricula_already_exists(client, json_headers, helpers, db_session, faker):
    user = helpers.create_user(db_session, faker)[0]

    body = {
        "username": "test-user-name",
        "email": "test.email@gmai.com",
        "matricula": user.matricula,
        "campus": "SEDE",
        "password": "123456",
        "curso": "CC"
    }

    response = client.post(REGISTER, headers=json_headers, json=body)

    error_msg = 'Essa matrícula já está cadastrado no sistema.'
    assert response.status_code == 409
    assert error_msg in response.text


def test_user_login_success(client, helpers, db_session, faker, json_headers):
    response = client.get(GET_FAV_ADS)
    assert response.status_code == 401

    user, password = helpers.create_user(db_session, faker)

    body = {
        "username": user.username,
        "password": password
    }

    login = client.post(LOGIN, headers=json_headers, json=body)
    login_json = login.json

    assert login.status_code == 200
    assert login_json['access_token']

    # verify that token works
    access_token = login_json['access_token']
    headers = helpers.bearer_header(access_token)

    auth_response = client.get(GET_FAV_ADS, headers=headers)

    assert auth_response.status_code == 200


def test_user_login_fail(client, helpers, db_session, faker, json_headers):
    user, password = helpers.create_user(db_session, faker)

    body_password = {
        "username": user.username,
        "password": 'wrong-password'
    }

    body_username = {
        "username": user.username + '123',
        "password": password,
    }

    response = client.post(LOGIN, headers=json_headers, json=body_password)
    invalid_credentials = 'Invalid credentials'

    assert response.status_code == 401
    assert invalid_credentials in response.text

    response = client.post(LOGIN, headers=json_headers, json=body_username)

    assert response.status_code == 401
    assert invalid_credentials in response.text


def test_user_logout_success(client, helpers, db_session, faker, json_headers):
    user, password = helpers.create_user(db_session, faker)

    body = {
        "username": user.username,
        "password": password
    }

    login = client.post(LOGIN, headers=json_headers, json=body)
    token = login.json['access_token']
    headers = helpers.bearer_header(token)

    logout = client.delete(LOGOUT, headers=headers)
    logout_msg = 'JWT revogado.'

    assert logout.status_code == 200
    assert logout_msg in logout.text

    revoked_response = client.get(GET_FAV_ADS, headers=headers)
    revoked_msg = 'Token has been revoked'

    assert revoked_response.status_code == 401
    assert revoked_msg in revoked_response.text


def test_search_books_with_filters(client, db_session, json_headers, faker, helpers):
    # Cria alguns anúncios de livros de teste no banco de dados
    user, password = helpers.create_user(db_session, faker)

    livro1 = AnuncioLivro(titulo='Livro 1', anunciante=user.username, descricao='Descrição 1',
                          preco=10.0, status=StatusAnuncio.AGUARDANDO_ACAO,
                          titulo_livro='Livro A', autor='Autor X', genero='Ficção', aceita_trocas=True)

    livro2 = AnuncioLivro(titulo='Livro 2', anunciante=user.username, descricao='Descrição 2',
                          preco=20.0, status=StatusAnuncio.AGUARDANDO_ACAO,
                          titulo_livro='Livro B', autor='Autor Y', genero='Não Ficção', aceita_trocas=False)

    db_session.add_all([livro1, livro2])
    db_session.commit()

    # Filtros para a pesquisa de livros
    filters = {
        'titulo_livro': 'A',
        'genero': 'Ficção',
        'preco_max': 15.0,
        'aceita_trocas': True
    }

    response = client.get(SEARCH_BOOKS, headers=json_headers, json=filters)
    assert response.status_code == 200

    data = response.json
    assert len(data) == 1

    livro = data[0]
    assert livro['titulo'] == 'Livro 1'
    assert livro['preco'] == 10.0
    assert livro['titulo_livro'] == 'Livro A'
    assert livro['autor'] == 'Autor X'
    assert livro['genero'] == 'Ficção'
    assert livro['aceita_trocas'] is True


def test_search_books_without_filters(client, db_session, json_headers, faker, helpers):
    # Cria alguns anúncios de livros de teste no banco de dados
    user, password = helpers.create_user(db_session, faker)

    livro1 = AnuncioLivro(titulo='Livro 1', anunciante=user.username, descricao='Descrição 1',
                          preco=10.0, status=StatusAnuncio.AGUARDANDO_ACAO,
                          titulo_livro='Livro A', autor='Autor A', genero='Gênero A', aceita_trocas=True)

    livro2 = AnuncioLivro(titulo='Livro 2', anunciante=user.username, descricao='Descrição 2',
                          preco=20.0, status=StatusAnuncio.AGUARDANDO_ACAO,
                          titulo_livro='Livro B', autor='Autor B', genero='Gênero B', aceita_trocas=False)

    db_session.add_all([livro1, livro2])
    db_session.commit()

    response = client.get(SEARCH_BOOKS, headers=json_headers)
    assert response.status_code == 200

    data = response.json
    assert len(data) == 2

    livro_1 = data[0]
    assert livro_1['titulo'] == 'Livro 1'
    assert livro_1['preco'] == 10.0
    assert livro_1['titulo_livro'] == 'Livro A'
    assert livro_1['autor'] == 'Autor A'
    assert livro_1['genero'] == 'Gênero A'
    assert livro_1['aceita_trocas'] is True

    livro_2 = data[1]
    assert livro_2['titulo'] == 'Livro 2'
    assert livro_2['preco'] == 20.0
    assert livro_2['titulo_livro'] == 'Livro B'
    assert livro_2['autor'] == 'Autor B'
    assert livro_2['genero'] == 'Gênero B'
    assert livro_2['aceita_trocas'] is False


def test_search_apartments_with_filters(client, db_session, json_headers, faker, helpers):
    user, password = helpers.create_user(db_session, faker)

    # Cria alguns anúncios de apartamentos de teste no banco de dados
    apartamento1 = AnuncioApartamento(titulo='Apartamento 1', anunciante=user.username, descricao='Descrição 1',
                                      preco=1000.0,
                                      status=StatusAnuncio.AGUARDANDO_ACAO, endereco='Endereço 1', area=50, comodos=2)
    apartamento2 = AnuncioApartamento(titulo='Apartamento 2', anunciante=user.username, descricao='Descrição 2',
                                      preco=2000.0,
                                      status=StatusAnuncio.AGUARDANDO_ACAO, endereco='Endereço 2', area=80, comodos=3)
    db_session.add_all([apartamento1, apartamento2])
    db_session.commit()

    # Filtros para a pesquisa de apartamentos
    filters = {
        'endereco': 'Endereço 1',
        'valor_max': 1500.0,
        'num_comodos': 2
    }

    response = client.get(SEARCH_APARTMENTS, headers=json_headers, json=filters)
    assert response.status_code == 200

    data = response.json
    assert len(data) == 1

    apartamento = data[0]
    assert apartamento['titulo'] == 'Apartamento 1'
    assert apartamento['preco'] == 1000.0
    assert apartamento['comodos'] == 2


def test_search_apartments_without_filters(client, db_session, json_headers, faker, helpers):
    # Cria alguns anúncios de apartamentos de teste no banco de dados
    user, password = helpers.create_user(db_session, faker)

    # Cria alguns anúncios de apartamentos de teste no banco de dados
    apartamento1 = AnuncioApartamento(titulo='Apartamento 1', anunciante=user.username, descricao='Descrição 1',
                                      preco=1000.0,
                                      status=StatusAnuncio.AGUARDANDO_ACAO, endereco='Endereço 1', area=50, comodos=2)
    apartamento2 = AnuncioApartamento(titulo='Apartamento 2', anunciante=user.username, descricao='Descrição 2',
                                      preco=2000.0,
                                      status=StatusAnuncio.AGUARDANDO_ACAO, endereco='Endereço 2', area=80, comodos=3)
    db_session.add_all([apartamento1, apartamento2])
    db_session.commit()

    response = client.get(SEARCH_APARTMENTS, headers=json_headers)
    assert response.status_code == 200

    data = response.json
    assert len(data) == 2

    apartamento_1 = data[0]
    assert apartamento_1['titulo'] == 'Apartamento 1'
    assert apartamento_1['preco'] == 1000.0
    assert apartamento_1['comodos'] == 2

    apartamento_2 = data[1]
    assert apartamento_2['titulo'] == 'Apartamento 2'
    assert apartamento_2['preco'] == 2000.0
    assert apartamento_2['comodos'] == 3

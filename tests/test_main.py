from models.model import User, AnuncioLivro, AnuncioApartamento, StatusAnuncio
from conf.config import (
    REGISTER,
    LOGIN,
    LOGOUT,
    CREATE_AD,
    UPDATE,
    DELETE_AD,
    GET_FAV_ADS,
    SEARCH_BOOKS,
    SEARCH_APARTMENTS,
    FAV_AD
)



def test_fav_ad_success(client, helpers, db_session, faker, json_headers):
    user, password = helpers.create_user(db_session, faker)
    access_token = helpers.login_user(user, password, client, json_headers)
    json_headers['Authorization'] = f'Bearer {access_token}'

    apartamento1 = {
        'titulo': 'Apartamento 1',
        'anunciante': user,
        'descricao': 'Descrição 1',
        'preco': 1000.0,
        'status': StatusAnuncio.AGUARDANDO_ACAO,
        'endereco': 'Endereço 1',
        'area': 50,
        'comodos': 2
    }
    ad = helpers.create_ap_ad(db_session, apartamento1)

    favorite = {
        "anuncio_id": ad.id
    }

    response = client.post(FAV_AD, headers=json_headers, json=favorite)

    assert response.status_code == 200

    ad_fav = user.anuncios_favoritos[0]
    assert ad_fav.id == ad.id


def test_fav_ad_already_favorited(client, helpers, db_session, faker, json_headers):
    user, password = helpers.create_user(db_session, faker)
    access_token = helpers.login_user(user, password, client, json_headers)
    json_headers['Authorization'] = f'Bearer {access_token}'

    apartamento1 = {
        'titulo': 'Apartamento 1',
        'anunciante': user,
        'descricao': 'Descrição 1',
        'preco': 1000.0,
        'status': StatusAnuncio.AGUARDANDO_ACAO,
        'endereco': 'Endereço 1',
        'area': 50,
        'comodos': 2
    }

    ad = helpers.create_ap_ad(db_session, apartamento1)
    favorite = {
        "anuncio_id": ad.id
    }
    client.post(FAV_AD, header=json_headers, json=favorite)
    response = client.post(FAV_AD, header=json_headers, json=favorite)

    error_msg = "O anúncio já está nos favoritos do usuário."
    assert response.status_code == 400
    assert error_msg in response.text


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

    livro1 = {
        'titulo': 'Livro 1',
        'anunciante': user,
        'descricao': 'Descrição 1',
        'preco': 10.0,
        'titulo_livro': 'Livro A',
        'autor': 'Autor X',
        'genero': 'Ficção',
        'aceita_trocas': True
    }

    livro2 = {
        'titulo': 'Livro 2',
        'anunciante': user,
        'descricao': 'Descrição 2',
        'preco': 20.0,
        'titulo_livro': 'Livro B',
        'autor': 'Autor Y',
        'genero': 'Não-Ficção',
        'aceita_trocas': False
    }

    helpers.create_book_ad(db_session, livro1)
    helpers.create_book_ad(db_session, livro2)

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
    # deleta items intrinsecamente diferentes do dicionario
    del livro['status'], livro['anunciante'], livro1['anunciante']
    assert livro == livro1


def test_search_books_without_filters(client, db_session, json_headers, faker, helpers):
    # Cria alguns anúncios de livros de teste no banco de dados
    user, password = helpers.create_user(db_session, faker)

    livro1 = {
        'titulo': 'Livro 1',
        'anunciante': user,
        'descricao': 'Descrição 1',
        'preco': 10.0,
        'titulo_livro': 'Livro A',
        'autor': 'Autor X',
        'genero': 'Ficção',
        'aceita_trocas': True
    }

    livro2 = {
        'titulo': 'Livro 2',
        'anunciante': user,
        'descricao': 'Descrição 2',
        'preco': 20.0,
        'titulo_livro': 'Livro B',
        'autor': 'Autor Y',
        'genero': 'Não-Ficção',
        'aceita_trocas': False
    }

    helpers.create_book_ad(db_session, livro1)
    helpers.create_book_ad(db_session, livro2)

    response = client.get(SEARCH_BOOKS, headers=json_headers, json={})
    assert response.status_code == 200

    data = response.json
    assert len(data) == 2

    livro_1 = data[0]
    del livro_1['status'], livro_1['anunciante'], livro1['anunciante']
    assert livro1 == livro_1

    livro_2 = data[1]
    del livro_2['status'], livro_2['anunciante'], livro2['anunciante']
    assert livro2 == livro_2


def test_search_apartments_with_filters(client, db_session, json_headers, faker, helpers):
    user, password = helpers.create_user(db_session, faker)

    apartamento1 = {
        'titulo': 'Apartamento 1',
        'anunciante': user,
        'descricao': 'Descrição 1',
        'preco': 1000.0,
        'status': StatusAnuncio.AGUARDANDO_ACAO,
        'endereco': 'Endereço 1',
        'area': 50,
        'comodos': 2
    }

    apartamento2 = {
        'titulo': 'Apartamento 2',
        'anunciante': user,
        'descricao': 'Descrição 2',
        'preco': 2000.0,
        'status': StatusAnuncio.AGUARDANDO_ACAO,
        'endereco': 'Endereço 2',
        'area': 80,
        'comodos': 3
    }
    helpers.create_ap_ad(db_session, apartamento1)
    helpers.create_ap_ad(db_session, apartamento2)

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

    apartamento1 = {
        'titulo': 'Apartamento 1',
        'anunciante': user,
        'descricao': 'Descrição 1',
        'preco': 1000.0,
        'status': StatusAnuncio.AGUARDANDO_ACAO,
        'endereco': 'Endereço 1',
        'area': 50,
        'comodos': 2
    }

    apartamento2 = {
        'titulo': 'Apartamento 2',
        'anunciante': user,
        'descricao': 'Descrição 2',
        'preco': 2000.0,
        'status': StatusAnuncio.AGUARDANDO_ACAO,
        'endereco': 'Endereço 2',
        'area': 80,
        'comodos': 3
    }
    helpers.create_ap_ad(db_session, apartamento1)
    helpers.create_ap_ad(db_session, apartamento2)
    response = client.get(SEARCH_APARTMENTS, headers=json_headers, json={})
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

# -------------------------------------------------------------------------------

def test_create_ad_livro(client, db_session, helpers, faker, json_headers):

    user, password = helpers.create_user(db_session, faker)
    access_token = helpers.login_user(user, password, client, json_headers)

    json_headers['Authorization'] = f'Bearer {access_token}'
    
    body = {
        "titulo": "Livro de estatística aplicada",
        "descricao": "Livro em perfeito estado, nunca usado",
        "preco": "300",
        "categoria": "livro",
        "tituloLivro": "Estatística Básica",
        "autor": "Bussab e Morettin",
        "genero": "Educação",
        "aceitaTroca": "True"
    }
     
    response = client.post(CREATE_AD, headers=json_headers, json=body)
    
    assert response.status_code == 201

    ad = db_session.query(AnuncioLivro).first()
    
    assert ad.titulo == body['titulo']
    assert ad.descricao == body['descricao']
    assert ad.preco == float(body['preco'])
    assert ad.titulo_livro == body['tituloLivro']
    assert ad.autor == body['autor']
    assert ad.genero == body['genero']
    assert ad.aceita_trocas == True
    

def test_create_ad_apartamento(client, db_session, helpers, faker, json_headers):

    user, password = helpers.create_user(db_session, faker)
    access_token = helpers.login_user(user, password, client, json_headers)

    json_headers['Authorization'] = f'Bearer {access_token}'
    
    body = {
        "titulo": "Apartamento 3 quartos perto da ufcg",
        "descricao": "apartamendo a 200m da ufcg com area de lazer e portaria",
        "preco": 1000,
        "categoria": "apartamento",
        "endereco": "Rua de Teste, 325, Universitário",
        "area": 120,
        "comodos": 9
    }
     
    response = client.post(CREATE_AD, headers=json_headers, json=body)
    
    assert response.status_code == 201

    ad = db_session.query(AnuncioApartamento).first()
    
    assert ad.titulo == body['titulo']
    assert ad.descricao == body['descricao']
    assert ad.preco == float(body['preco'])
    assert ad.endereco == body['endereco']
    assert ad.area == int(body['area'])
    assert ad.comodos == int(body['comodos'])
    

def test_create_ad_categoria_invalida(client, db_session, helpers, faker, json_headers):

    user, password = helpers.create_user(db_session, faker)
    access_token = helpers.login_user(user, password, client, json_headers)

    json_headers['Authorization'] = f'Bearer {access_token}'

    body = {
        "titulo": "Livro de estatística aplicada",
        "descricao": "Livro em perfeito estado, nunca usado",
        "preco": "300",
        "categoria": "Piscina",
        "tituloLivro": "Estatística Básica",
        "autor": "Bussab e Morettin",
        "genero": "Educação",
        "aceitaTroca": "True"
    }
   
    response = client.post(CREATE_AD, headers=json_headers, json=body)
    
    assert response.status_code == 400


def test_create_ad_campos_incompletos(client, db_session, helpers, faker, json_headers):

    user, password = helpers.create_user(db_session, faker)
    access_token = helpers.login_user(user, password, client, json_headers)

    json_headers['Authorization'] = f'Bearer {access_token}'

    body = {
        "titulo": None,
        "descricao": "apartamendo a 200m da ufcg com area de lazer e portaria",
        "preco": 1000,
        "categoria": "apartamento",
        "endereco": "Rua de Teste, 325, Universitário",
        "area": 120,
        "comodos": 9
    }
   
    response = client.post(CREATE_AD, headers=json_headers, json=body)
    
    assert response.status_code == 400
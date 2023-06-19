from models.model import StatusAnuncio
from conf.config import (
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
    client.post(FAV_AD, headers=json_headers, json=favorite)
    response = client.post(FAV_AD, headers=json_headers, json=favorite)

    error_msg = "O anúncio já está nos favoritos do usuário."
    assert response.status_code == 400
    assert error_msg in response.text


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
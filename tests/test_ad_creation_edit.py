import uuid

from models.model import AnuncioLivro, AnuncioApartamento, StatusAnuncio, Anuncio
from conf.config import (
    CREATE_AD,
    EDIT_AD,
    SEARCH_APARTMENTS
)


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


def test_edit_ad(client, db_session, helpers, faker, json_headers):

    user, password = helpers.create_user(db_session, faker)
    access_token = helpers.login_user(user, password, client, json_headers)

    json_headers['Authorization'] = f'Bearer {access_token}'

    apartamento = {
        'titulo': 'Apartamento 1',
        'anunciante': user,
        'descricao': 'Descrição 1',
        'preco': 1000.0,
        'status': StatusAnuncio.AGUARDANDO_ACAO,
        'endereco': 'Endereço 1',
        'area': 50,
        'comodos': 2
    }

    ad = helpers.create_ap_ad(db_session, apartamento)

    edit = {
        'id_anuncio': ad.id,
        'descricao': str(uuid.uuid4()),
        'categoria': 'apartamento'
    }

    response = client.put(EDIT_AD, headers=json_headers, json=edit)
    edited_ads = client.get(SEARCH_APARTMENTS, json={})

    assert response.status_code == 200
    assert edit['descricao'] in edited_ads.text
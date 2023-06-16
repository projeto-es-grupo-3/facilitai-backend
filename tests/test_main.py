from models.model import User
from conf.config import (
    REGISTER,
    LOGIN,
    LOGOUT,
    CREATE_AD,
    UPDATE,
    DELETE_AD,
    GET_FAV_ADS
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

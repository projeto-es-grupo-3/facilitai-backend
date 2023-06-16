from models.model import User
from conf.config import (
    REGISTER,
    LOGIN,
    LOGOUT,
    CREATE_AD,
    UPDATE,
    DELETE_AD
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
    user = helpers.create_user(db_session, faker)
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
    user = helpers.create_user(db_session, faker)
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
    user = helpers.create_user(db_session, faker)
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
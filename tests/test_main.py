from models.model import User
from conf.config import (
    REGISTER,
    LOGIN,
    LOGOUT,
    CREATE_AD,
    UPDATE,
    DELETE_AD
)


def test_user_register_success(client, db_session):
    headers = {'Content-Type': 'application/json'}
    body = {
        "username": "test-user-name",
        "email": "test.email@gmai.com",
        "matricula": "110110110",
        "campus": "SEDE",
        "password": "123456",
        "curso": "CC"
    }

    response = client.post(REGISTER, headers=headers, json=body)

    assert response.status_code == 201

    user = db_session.query(User).first()
    assert user.email == body['email']
    assert user.username == body['username']
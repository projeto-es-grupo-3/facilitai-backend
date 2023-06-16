from werkzeug.security import generate_password_hash

from models.model import User


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
    def bearer_header(token):
        return {'Authorization': f"Bearer {token}"}
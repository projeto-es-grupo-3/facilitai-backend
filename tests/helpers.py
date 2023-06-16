from werkzeug.security import generate_password_hash

from models.model import User


class Helpers:
    @staticmethod
    def create_user(db_session, faker):
        password = generate_password_hash("12345678", method="sha256")
        email = faker.email()

        new_user = User(
            'user.name',
            email,
            '120120120',
            'CG',
            password,
            'CC'
        )

        db_session.add(new_user)
        db_session.commit()

        return new_user
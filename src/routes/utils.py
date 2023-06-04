from models.model import db


def increase_rating(current_user):
    """
    Aumenta o rating do usuário para cada troca/venda
    """
    user = current_user # Esse usuário é realamente o usuário atual ?

    rating = user.rating
    rating += 1

    db.commit()

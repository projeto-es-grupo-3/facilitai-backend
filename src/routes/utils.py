from models.model import db

def increase_rating(ad_id):
    """
    Aumenta o rating do usuário para cada troca/venda
    """

    ad = Anuncio.query.get(ad_id)

    user_id = ad.user_id
    user = User.query.get(user_id)

    if user is None:
        return f"User with id {user_id} was not found.", 404

    user.rating += 1

    db.commit()

import uuid

from pathlib import Path
from flask import Blueprint, request, jsonify, abort, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token, current_user, jwt_required, JWTManager, get_jwt
from datetime import datetime, timezone
from dataclasses import asdict
import json


from models.model import (
    User,
    db,
    Anuncio,
    AnuncioLivro,
    AnuncioApartamento,
    Anuncio,
    StatusAnuncio,
    TokenBlockList
)
from conf.config import (
    REGISTER,
    LOGIN,
    LOGOUT,
    CREATE_AD,
    UPDATE,
    DELETE_AD,
    EDIT_AD,
    UPLOAD_IMG_AD,
    UPLOAD_PROFILE_IMG,
    IMAGE_PATH,
    IMAGE,
    FAV_AD,
    GET_FAV_ADS,
    SEARCH_BOOKS,
    SEARCH_APARTMENTS
)

bp = Blueprint('bp', __name__, template_folder='templates', url_prefix='')


def init_jwt(app):
    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.username

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        username = jwt_data["sub"]
        return User.query.filter_by(username=username).one_or_none()

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token = TokenBlockList.query.filter_by(jti=jti).scalar()

        return token is not None


@bp.route(REGISTER, methods=['POST'])
def register():
    """Cria um novo usuário no sistema.

    Returns:
        Um objeto JSON com a mensagem de sucesso e código 201.

    Raises:
        BadRequest: Se algum dos campos necessários não for fornecido ou se a matrícula fornecida não for válida.
        Conflict: Se o nome de usuário, email ou matrícula já estiverem sendo usados por outro usuário.
    """

    username = request.json["username"]
    email = request.json["email"]
    matricula = request.json["matricula"]
    campus = request.json["campus"]
    password = request.json["password"]
    curso = request.json["curso"]

    # Verifica se todos os campos necessários foram fornecidos
    if not all([username, email, matricula, campus, password, curso]):
        abort(400, 'Todos os campos precisam ser preenchidos.')

    # Verifica se a matrícula fornecida tem o formato correto
    if len(matricula) != 9:
        abort(400, 'Matricula Inválida')

    # Verifica se o nome de usuário, email ou matrícula já estão em uso por outro usuário
    if User.query.filter_by(username=username).first():
        abort(409, 'Esse usuario já está cadastrado no sistema.')

    if User.query.filter_by(email=email).first():
        abort(409, 'Esse e-mail já está cadastrado no sistema.')

    if User.query.filter_by(matricula=matricula).first():
        abort(409, 'Essa matrícula já está cadastrado no sistema.')

    # Cria o novo usuário e salva no banco de dados
    new_user = User(username, email, matricula, campus, generate_password_hash(password), curso)
    db.session.add(new_user)
    db.session.commit()

    # Retorna a mensagem de sucesso com o código 201
    return jsonify(message='Usuário cadastrado com sucesso.'), 201


@bp.route(CREATE_AD, methods=['POST'])
@jwt_required()
def create_ad():
    """Cria um novo anúncio no sistema.

    Returns:
        Um objeto JSON com a mensagem de sucesso e código 201.

    Raises:
        BadRequest: Se algum dos campos necessários não for fornecido.
        Unauthorized: Se o usuário não estiver logado.
    """
    titulo = request.json.get("titulo", None)
    descricao = request.json.get("descricao", None)
    preco = float(request.json.get("preco", None))
    categoria = request.json.get("categoria", None)
    # imagens = request.files.getlist('imagens')
    anunciante = current_user
    status = StatusAnuncio.AGUARDANDO_ACAO

    if not categoria: abort(400, 'Categoria é necessária.')
    if not anunciante: abort(401, 'O usuário precisa estar logado.')

    if categoria == 'livro':
        titulo_livro = request.json.get('tituloLivro', None)
        autor = request.json.get('autor', None)
        genero = request.json.get('genero', None)
        aceita_trocas = request.json.get('aceitaTroca', False)

        if not all([titulo, descricao, preco, titulo_livro, genero, autor]): abort(400, 'Todos os campos precisam ser preenchidos.')

        new_livro = AnuncioLivro(titulo, anunciante, descricao, preco, status, titulo_livro, autor, genero, bool(aceita_trocas)) 
        
        db.session.add(new_livro)
        db.session.commit()

    elif categoria == 'apartamento':
        endereco = request.json.get('endereco', None)
        area = int(request.json.get('area', None))
        comodos = int(request.json.get('comodos', None))

        if not all([titulo, descricao, preco, endereco, area, comodos]): abort(400,
                                                                               'Todos os campos precisam ser preenchidos.')
        new_apartament = AnuncioApartamento(titulo, anunciante, descricao, preco, status, endereco, area, comodos)
        
        db.session.add(new_apartament)
        db.session.commit()
    
    else: 
        abort(400, 'Não existem anuncios dessa categoria')

    return jsonify(message='Anúncio criado.'), 201


@bp.route(EDIT_AD, methods=['PUT'])
@jwt_required()
def edit_ad():
    """
    Edita um anúncio existente.

    Args:
        id: O ID do anúncio a ser editado.

    Returns:
        Um objeto JSON com a mensagem de sucesso e código 200.

    Raises:
        NotFound: Se o anúncio não for encontrado.
        Unauthorized: Se o usuário não estiver autorizado a editar o anúncio.
    """
    anuncio = Anuncio.query.get(request.json.get('id_anuncio'))

    if not anuncio: abort(404, 'Anúncio não encontrado')
    if anuncio.anunciante != current_user: abort(401, 'Usuário não autorizado para editar este anúncio')

    categoria = request.json.get("categoria", None)
    titulo = request.json.get("titulo", None)
    descricao = request.json.get("descricao", None)
    preco = request.json.get("preco", None)
    status = request.json.get("status", None)

    if titulo: anuncio.titulo = titulo
    if descricao: anuncio.descricao = descricao
    if preco: anuncio.preco = float(preco)
    if status: anuncio.status = StatusAnuncio(status)

    if categoria == 'livro':
        titulo_livro = request.json.get('titulo_livro', None)
        autor = request.json.get('autor', None)
        genero = request.json.get('genero', None)
        aceita_trocas = request.json.get('aceita_trocas', None)

        if titulo_livro: anuncio.titulo_livro = titulo_livro
        if autor: anuncio.autor = autor
        if genero: anuncio.genero = genero
        if aceita_trocas: anuncio.aceita_trocas = aceita_trocas

    elif categoria == 'apartamento':
        endereco = request.json.get('endereco', None)
        area = request.json.get('area', None)
        comodos = request.json.get('comodos', None)

        if endereco: anuncio.endereco = endereco
        if area: anuncio.area = area
        if comodos: anuncio.comodos = comodos

    else: 
        abort(400, 'Não existem anuncios dessa categoria')

    db.session.commit()

    return jsonify(message="Anúncio editado com sucesso"), 200

  
@bp.route(LOGIN, methods=["POST"])
def login():
    """
    Endpoint que permite logar no sistema, caso o usuário esteja cadastrado.
    As informações utilizadas para realizar o login são: email e senha.

    Returns:
        Um objeto JSON contendo uma mensagem de sucesso caso a atualização seja realizada com sucesso.
    """
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.pass_hash, password):
        access_token = create_access_token(identity=user)
        return jsonify(message="Logado com sucesso", access_token=access_token)

    return jsonify("Invalid credentials"), 401


@bp.route(UPDATE, methods=['POST'])
@jwt_required()
def update_user():
    """
    Endpoint que permite a atualização das informações de um usuário cadastrado.
    As informações que podem ser atualizadas são: nome de usuário, campus, senha e curso.

    Returns:
        Um objeto JSON contendo uma mensagem de sucesso caso a atualização seja realizada com sucesso.

    Raises:
        HTTPException: uma exceção é levantada caso o usuário não esteja autenticado ou as informações
        enviadas na requisição sejam inválidas.
    """

    # Obtém o usuário atual a partir da sessão
    user = current_user

    # Verifica se o usuário está autenticado
    if not user:
        abort(401, 'Nenhum usuário logado.')

    # Obtém as informações a serem atualizadas a partir do JSON enviado na requisição
    new_username = request.json['username']
    new_campus = request.json["campus"]
    new_password = request.json["password"]
    new_curso = request.json["curso"]

    # Verifica se o username já existe para outro usuário
    existing_username_user = User.query.filter_by(username=new_username).first()

    if existing_username_user and existing_username_user != user:
        abort(409, 'Nome de usuário indisponível.')

    # Atualiza as informações do usuário com as novas informações, se elas foram fornecidas
    if new_username:
        user.username = new_username

    if new_campus:
        user.campus = new_campus

    if new_password:
        user.pass_hash = generate_password_hash(new_password)

    if new_curso:
        user.curso = new_curso

    db.session.commit()

    return jsonify(message='Usuário atualizado com sucesso.'), 204


@bp.route(SEARCH_BOOKS, methods=['GET'])
def search_books():

    # Iniciar com uma consulta base para recuperar os anúncios de livros
    query = AnuncioLivro.query
    filters = request.json

    # Obter os parâmetros de consulta da requisição
    if filters:
        nome_livro = filters.get('nome_livro', None)
        nome_autor = filters.get('nome_autor', None)
        genero = filters.get('genero', None)
        preco_min = filters.get('preco_min, None')
        preco_max = filters.get('preco_max', None)
        aceita_trocas = filters.get('aceita_trocas', None)


        # Aplicar filtros com base nos critérios do usuário
        if nome_livro:
            query = query.filter(AnuncioLivro.titulo_livro.ilike(f'%{nome_livro}%'))

        if nome_autor:
            query = query.filter(AnuncioLivro.autor.ilike(f'%{nome_autor}%'))

        if genero:
            query = query.filter(AnuncioLivro.genero.ilike(f'%{genero}%'))

        if preco_min:
            query = query.filter(AnuncioLivro.preco >= float(preco_min))

        if preco_max:
            query = query.filter(AnuncioLivro.preco <= float(preco_max))

        if aceita_trocas:
            query = query.filter(AnuncioLivro.aceita_trocas == aceita_trocas)

    # Executar a consulta e recuperar os anúncios de livros filtrados
    resultados = query.all()

    # Serializar cada anúncio de livro nos resultados e remover dados de anunciante
    livros_serial = [livro.get_to_dict() for livro in resultados]

    return jsonify(livros_serial)


@bp.route(SEARCH_APARTMENTS, methods=['GET'])
def search_apartments():
    """Realiza a filtragem de imóveis anunciados com base nos filtros fornecidos no JSON.

    O corpo da requisição pode conter um JSON com os seguintes campos opcionais:
        - endereco: Filtra por endereco do imóvel.
        - valor_min: Filtra por valor mínimo do imóvel.
        - valor_max: Filtra por valor máximo do imóvel.
        - num_comodos: Filtra por número de comodos do imóvel.

    Returns:
        Uma lista de imóveis filtrados em formato JSON.
    """
    filters = request.json
    query = AnuncioApartamento.query

    if filters:
        endereco = filters.get('endereco', None)
        valor_min = filters.get('valor_min', None)
        valor_max = filters.get('valor_max', None)
        num_comodos = filters.get('num_comodos', None)

        if endereco:
            query = query.filter(AnuncioApartamento.endereco.ilike(f'%{endereco}%'))

        if valor_min:
            query = query.filter(AnuncioApartamento.preco >= float(valor_min))

        if valor_max:
            query = query.filter(AnuncioApartamento.preco <= float(valor_max))

        if num_comodos:
            query = query.filter(AnuncioApartamento.comodos >= int(num_comodos))

    lista_apartamentos = query.all()

    apartamentos_json = [apartamento.get_to_dict() for apartamento in lista_apartamentos]

    return jsonify(apartamentos_json)


@bp.route(DELETE_AD, methods=['DELETE'])
@jwt_required()
def delete_ad():
    ad_id = request.json.get('id', None)

    if not ad_id: abort(400, 'O campo de ID deve ser preenchido.')

    ad = Anuncio.query.filter_by(id=ad_id).one_or_none()

    if not ad: abort(400, 'Anúncio não existe.')
    if not ad.is_from_user(current_user): abort(401, 'Anúncio deletável apenas por autor.')

    db.session.delete(ad)
    db.session.commit()

    return jsonify(message='Anúncio deletado.')


@bp.route(LOGOUT, methods=['DELETE'])
@jwt_required()
def logout():
    """
    Revoga o token de autenticação do usuário.
    """
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlockList(jti, now))
    db.session.commit()
    return jsonify(msg="JWT revogado.")


@bp.route(FAV_AD, methods=['POST'])
@jwt_required()
def fav_ad():
    anuncio_id = request.json.get('anuncio_id')
    anuncio = Anuncio.query.get(anuncio_id)
    # Obtém o usuário atual a partir da sessão
    user = current_user

    # Verifica se o usuário está autenticado
    if not user:
        abort(401, 'Nenhum usuário logado.')
    if not anuncio:
        abort(401, 'O anúncio não foi encontrado')
    if anuncio in user.anuncios_favoritos:
        abort(400, 'O anúncio já está nos favoritos do usuário.')

    user.anuncios_favoritos.append(anuncio)
    db.session.commit()

    return jsonify(message='Anúncio favoritado com sucesso.'), 200


@bp.route(GET_FAV_ADS, methods=['GET'])
@jwt_required()
def get_favorited_anuncios():
    user = current_user
    if not user:
        abort(401, 'Nenhum usuário logado.')

    anuncios_favoritados = user.anuncios_favoritos

    favoritos = [anuncio.get_to_dict() for anuncio in anuncios_favoritados]

    return jsonify(favoritos)


@bp.route(UPLOAD_IMG_AD, methods=['POST'])
@jwt_required()
def upload_image_ad():
    ad_id = request.form.get('ad_id')
    img = request.files['ad_img']
    img_filename = secure_filename(img.filename)
    real_filename = str(uuid.uuid1()) + '_' + img_filename

    image_path = Path(IMAGE_PATH + real_filename).expanduser()

    img.save(image_path)

    ad = Anuncio.query.get(ad_id)
    ad.ad_img = real_filename

    db.session.commit()

    image_location = url_for('bp.get_image', file_name=real_filename, _external=True)

    return jsonify(message='Image uploaded.'), 200, {'Location': image_location}


@bp.route(UPLOAD_PROFILE_IMG, methods=['POST'])
@jwt_required()
def upload_profile_picture():
    img = request.files['profile_img']
    img_filename = secure_filename(img.filename)
    real_filename = str(uuid.uuid1()) + '_' + img_filename

    image_path = Path(IMAGE_PATH + real_filename).expanduser()

    img.save(image_path)

    user = User.query.get(current_user.id)
    user.profile_img = real_filename

    db.session.commit()

    image_location = url_for('bp.get_image', file_name=real_filename, _external=True)

    return jsonify(message='Image uploaded.'), 200, {'Location': image_location}


@bp.route(IMAGE, methods=['GET'])
@jwt_required()
def get_image(file_name):
    return send_file(Path(IMAGE_PATH + file_name).expanduser(), mimetype='image/png')

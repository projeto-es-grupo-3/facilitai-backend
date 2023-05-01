from flask import Blueprint, request, jsonify, session, abort
from werkzeug.security import generate_password_hash, check_password_hash

from .model import (
    User,
    db,
    AnuncioLivro,
    AnuncioApartamento
)

bp = Blueprint('bp', __name__, template_folder='templates', url_prefix='')

def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


@bp.route('/register', methods=['POST'])
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


@bp.route('/create_ad', methods=['POST'])
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
    anunciante = current_user()

    if not categoria: abort(400, 'Categoria é necessária.')
    if not anunciante: abort(401, 'O usuário precisa estar logado.')

    if categoria == 'livro':
        titulo_livro = request.json.get('tituloLivro', None)
        autor = request.json.get('autor', None)
        genero = request.json.get('genero', None)

        if not all([titulo, descricao, preco, titulo_livro, genero]): abort(400, 'Todos os campos precisam ser preenchidos.')

        new_livro = AnuncioLivro(titulo, anunciante, descricao, preco, titulo_livro, autor, genero) 
        
        db.session.add(new_livro)
        db.session.commit()   
    
    elif categoria == 'apartamento':
        endereco = request.json.get('endereco', None)
        area = int(request.json.get('area', None))
        comodos = int(request.json.get('comodos', None))

        if not all([titulo, descricao, preco, endereco, area, comodos]): abort(400, 'Todos os campos precisam ser preenchidos.')

        new_apartament = AnuncioApartamento(titulo, anunciante, descricao, preco, endereco, area, comodos)
        
        db.session.add(new_apartament)
        db.session.commit()

    return jsonify(message='Anúncio criado.'), 201


@bp.route('/login', methods=['POST'])
def login():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.pass_hash, password):
        session['id'] = user.id
        return jsonify("Logado com sucesso."), 200
    
    return jsonify("Credenciais Inválidas"), 401


@bp.route('/update', methods=['POST'])
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
    user = current_user()

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

@bp.route('/logout')
def logout():
    del session['id']

from flask import Blueprint, request, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, current_user, jwt_required, JWTManager, get_jwt
from datetime import datetime, timezone

from .model import (
    User,
    db,
    AnuncioLivro,
    AnuncioApartamento,
    TokenBlockList
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


@bp.route("/login", methods=["POST"])
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


@bp.route('/update', methods=['POST'])
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

@bp.route('/logout', methods=['DELETE'])
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

@jwt_required
def notify():
    """
    Notifica o usuário sobre atualizações em anúncios.
    Esse método é chamado dentro de outros métodos, quando houverem atualizações em 
    anúncios do interesse do usuário.
    """

    user = current_user

    to_email = current_user.email
    subject = 'Houveram atualizações desde a sua última visita ao Facilitaí !'
    message = 'Olá ! Anúncios de seu interesse foram atualizados desde a sua última visita.'    

    if send_email_notification(to_email, subject, message):
        return 'Notification sent successfully'
    else:
        return 'Failed to send notification'

def send_email_notification(to_email, subject, message):
    from_email = 'facilitai-ufcg@gmail.com'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465
    username = "facilitai-ufcg"
    password = 'odeiojava123'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    body = message
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(str(e))
        return False

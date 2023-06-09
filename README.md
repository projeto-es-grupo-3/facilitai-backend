# Backend do Facilitaí

## Como executar
Para rodar o serviço localmente, as seguintes dependências são necessárias:

- **Python 3.10**: o executável `python3` deve estar disponível na máquina
- **PostgreSQL**: o PostgreSQL deve estar com suas configurações iniciais finalizadas

Com as dependências resolvidas e dentro do diretório do projeto:

```sh
# instala o gerenciador de projeto na máquina
make setup-poetry

# cria o ambiente virtual com poetry
make venv

# ativa o ambiente virtual
poetry shell

# roda o serviço
make run

# roda os testes
make test

# testa a cobertura e torna acessível o report de cobertura em htmlcov/index.html
make coverage
```

O serviço é hosteado, por default de Flask, na porta 5000 do localhost.

## Rotas disponíveis
As seguintes rotas estão implementadas:

### Registro
`POST /register` aceita objeto de registro de usuário no seguinte formato:
```json
{
    "username": "nome.usuario",
    "email": "email.usuario@gmail.com",
    "matricula": "120120120",
    "campus": "Campina Grande",
    "password": "senhasecreta",
    "curso": "CC"
}
```
### Criação de anúncio
`POST /create_ad Authorization: Berarer {access_token}` aceita dois objetos de criação de anúncio nos seguintes formatos:

- Anúncio de livro

```json
{
    "titulo": "Titulo de Anuncio",
    "descricao": "Livro novo lacrado edição de 2021",
    "preco": 20.0,
    "categoria": "livro",
    "titulo_livro": "Livro Legal",
    "autor": "Nome Autor",
    "genero": "Romance",
}
```

- Anúncio de apartamento

```json
{
    "titulo": "Titulo de Anuncio",
    "descricao": "Apartamento no bodocongó",
    "preco": 200.0,
    "categoria": "apartamento",
    "endereco": "R. Vigario Calixto, 342",
    "area": 22,
    "comodos": 2
}
```
### Login
`POST /login` aceita objeto de login de usuário no seguinte formato:
```json
{
    "username": "username.user",
    "password": "senhasecreta"
}
```
> Responde com json com token de autenticação `access_token`

### Atualização de usuário
`POST /update Authorization: Bearer {access_token}` aceita objeto de atualização de usuário no seguinte formato:
```json
{
    "username": "novo.username",
    "campus": "Patos",
    "password": "novasenhasecreta",
    "curso": "EE"
}
```
### Filtro de livros
`GET /search_books Authorization: Bearer {access_token}` filtra os livros de acordo com as escolhas do usuario, no seguinte formato:
```json
{
  "nome_livro": "As cronicas wenzin",
  "nome_autor": "wenzin",
  "genero": "aventura",
  "preco_min": 50,
  "preco_max": 200
}
```
## Filtro de apartamentos
`GET /search_apartaments Authorization: Bearer {access_token}` filtra os apartamentos de acordo com as escolhas do usuario, no seguinte formato:
```json
{
    "endereco": "r do wezin, n0",
    "valor_min": 200,
    "valor_max": 600,
    "num_comodos": 3
}
```
### Logout

`DELETE /logout Authorization: Bearer {access_token}` revoga o token de autenticação do usuário.


### Upload e acesso a imagens

Existem dois endpoints para o upload de imagens: um para upload de imagens de anúncios (apenas uma imagem por anúncio) e uma para o upload da imagem de perfil. Ambos os endpoints retornam o header `Location` com a localização da imagem no servidor.

- `POST /upload-image Authorization: Bearer {access_token}` recebe a imagem para o anúncio em `multipart/form-data`:
```
# em multipart/form-data
{
    "ad_id": 1,
    "ad_img": <imagem>
}
```

- `POST /upload-profile Authorization: Bearer {access_token}` recebe a imagem para a foto de perfil em `multipart/form-data`:
```
# em multipart/form-data
{
    "profile_img": <imagem>
}
```

> Para acessar imagens um request com `GET <Location> Authorization: Bearer {access_token}` consegue acessar a imagem.

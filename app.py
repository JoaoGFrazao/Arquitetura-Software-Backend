from flask import Flask, render_template, request, url_for, redirect, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from sqlalchemy import CheckConstraint
from model.boardgames import db, Boardgames, Partidas
from parse import parse_bgg_response, parse_bgg_add
import requests, os

app = Flask(__name__)
Swagger(app)

db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_dir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

#Rota principal com render para a página principal
@app.route('/')
def home():
    return render_template("home.html"), 200

#Rota para adicionar jogos ao BD
@app.route('/add_game', methods=['POST'])
def add():
    """
    Adicionar novo Boardgame.
    ---
    parameters:
      - name: nome
        in: formData
        type: string
        required: true
        description: O nome do Boardgame.
      - name: playerage
        in: formData
        type: integer
        required: true
        description: A idade mínima sugerida do jogador
      - name: playtime
        in: formData
        type: integer
        required: true
        description: O tempo médio de uma partida em minutos.
      - name: min_players
        in: formData
        type: integer
        required: true
        description: O número mínimo de jogadores.
      - name: max_players
        in: formData
        type: integer
        required: true
        description: O número máximo de jogadores.
      - name: ano_publi
        in: formData
        type: integer
        required: true
        description: Ano da publicação do jogo
    responses:
      200:
        description: Jogo adicionado com sucesso
      302:
        description: Redireciona para a página principal após adicionar o jogo.
      400:
        description: Erro se alguma informação faltar ou alguma constraint for desrespeitada.
    """
    nome = request.form.get('nome')
    playerage = request.form.get('playerage')
    playtime = request.form.get('playtime')
    min_players = request.form.get('min_players')
    max_players = request.form.get('max_players')
    ano_publi = request.form.get('ano_publi')

    if min_players > max_players and int(playtime) < 0:
      return "Máximo de jogadores maior que o mínimo e tempo de jogo inválido"
    elif min_players > max_players:
      return "Máximo de jogadores menor que o mínimo", 400
    elif int(playtime) < 0:
      return "Tempo de jogo inválido", 400
    else:
      bg = Boardgames(nome, playerage, playtime, min_players, max_players, ano_publi)
      db.session.add(bg)
      db.session.commit()

    return render_template("home.html")


#Rota para listar todos os boardgames do BD
@app.route('/list_all', methods=['GET'])
def list_boardgames():
    """
    Listar todos os Boardgames.
    ---
    responses:
      200:
        description: Uma lista de todos os Boardgames.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: O ID e Primary Key do Boardgame.
              Nome:
                type: string
                description: O nome do Boardgame.
              Idade Mínima Sugerida:
                type: integer
                description: A idade mínima sugerida do jogador
              Tempo de Jogo:
                type: integer
                description: O tempo médio de uma partida em minutos.
              Mínimo de Jogadores:
                type: integer
                description: O número mínimo de jogadores.
              Máximo de Jogadores:
                type: integer
                description: O número máximo de jogadores.
              Ano de Publicação:
                type: integer
                description: Ano da publicação do jogo
    """


    boardgames = Boardgames.query.all()
    boardgames_list = []
    
    for game in boardgames:
        game_data = {
            'id': game.id,
            'Nome': game.nome,
            'playerage': game.playerage,
            'Tempo de Jogo': game.playtime,
            'Mínimo de Jogadores': game.min_players,
            'Máximo de Jogadores': game.max_players,
            'Ano de Publicação': game.ano_publi
        }
        boardgames_list.append(game_data)
    if len(boardgames_list) == 0:
      return "Não existem boardgames cadastrados", 200 

    return jsonify(boardgames_list)

#Rota para excluir boardgames do BD
@app.route('/boardgames/<int:id>', methods=['DELETE'])
def delete(id):
    """
    Excluir um Boardgame pelo ID.
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: O ID do boardgame para ser deletado.
    responses:
      200:
        description: Boardgame deletado com sucesso.
      404:
        description: Boardgame não encontrado.
    """
    game_to_delete = Boardgames.query.get_or_404(id)
    db.session.delete(game_to_delete)
    db.session.commit()
    return jsonify({'message': 'Boardgame deletado com sucesso'})


@app.route('/search_game', methods=['GET'])
def search_game():
    """
    Pesquisar um Boardgame por nome na API BoardGameGeek.
    ---
    parameters:
      - name: name
        in: query
        type: string
        required: true
        description: O nome do Boardgame para ser pesquisado.
    responses:
      200:
        description: Retorna os resultados da pesquisa.
      400:
        description: Erro se o nome do jogo estiver faltando.
      500:
        description: Erro ao buscar dados na API BoardGameGeek.
    """
    game_name = request.args.get('name')
    if not game_name:
        return jsonify({'error': 'Missing game name'}), 400

    url = f'https://www.boardgamegeek.com/xmlapi2/search?query={game_name}&type=boardgame'
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data from BoardGameGeek API'}), 500

    games = parse_bgg_response(response.content)

    return jsonify(games)

@app.route('/add_game_bgg', methods=['POST'])
def add_game_bgg():
    """
    Adicionar um Boardgame usando o ID da BoardGameGeek API.
    ---
    parameters:
      - name: id
        in: body
        type: integer
        required: true
        description: O ID do jogo na BoardGameGeek API.
    responses:
      200:
        description: Jogo adicionado com sucesso.
      400:
        description: Erro se o ID do jogo estiver faltando.
      404:
        description: Jogo não encontrado.
      500:
        description: Erro ao buscar dados na API BoardGameGeek.
    """
    bgg_id = request.json.get('id')
    if not bgg_id:
        return jsonify({'error': 'Missing game ID'}), 400

    url = f'https://boardgamegeek.com/xmlapi2/thing?id={bgg_id}'
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data from BoardGameGeek API'}), 500

    game = parse_bgg_add(response.content)
    if not game:
        return jsonify({'error': 'Game not found'}), 404

    nome = game["name"]
    playerage = game["minage"]
    playtime = game["playingtime"]
    min_players = game["minplayers"]
    max_players = game["maxplayers"]
    ano_publi = game["yearpublished"]

    bg = Boardgames(nome, playerage, playtime, min_players, max_players, ano_publi)
    db.session.add(bg)
    db.session.commit()

    return jsonify({'message': 'Game added successfully', 'game': game})

@app.route('/get_boardgames', methods=['GET'])
def get_boardgames():
    """
    Retorna todos os Boardgames para preencher um select no HTML.
    ---
    responses:
      200:
        description: Uma lista de todos os Boardgames.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: O ID e Primary Key do Boardgame.
              nome:
                type: string
                description: O nome do Boardgame.
              min_players:
                type: integer
                description: O número mínimo de jogadores.
              max_players:
                type: integer
                description: O número máximo de jogadores.
    """
    boardgames = Boardgames.query.all()
    boardgames_list = [{'id': game.id, 'nome': game.nome, 'min_players': game.min_players, 'max_players': game.max_players} for game in boardgames]
    return jsonify(boardgames_list)

@app.route('/register_match', methods=['POST'])
def register_match():
    """
    Registrar uma nova partida.
    ---
    parameters:
      - name: boardgame_id
        in: formData
        type: integer
        required: true
        description: O ID do Boardgame.
      - name: data_partida
        in: formData
        type: string
        format: date
        required: true
        description: A data da partida no formato YYYY-MM-DD.
      - name: vencedor
        in: formData
        type: string
        required: true
        description: O nome do vencedor da partida.
      - name: jogador1
        in: formData
        type: string
        required: false
        description: Nome do jogador 1.
      - name: jogador2
        in: formData
        type: string
        required: false
        description: Nome do jogador 2.
      - name: jogador3
        in: formData
        type: string
        required: false
        description: Nome do jogador 3.
      - name: jogador4
        in: formData
        type: string
        required: false
        description: Nome do jogador 4.
      - name: jogador5
        in: formData
        type: string
        required: false
        description: Nome do jogador 5.
      - name: jogador6
        in: formData
        type: string
        required: false
        description: Nome do jogador 6.
      - name: jogador7
        in: formData
        type: string
        required: false
        description: Nome do jogador 7.
      - name: jogador8
        in: formData
        type: string
        required: false
        description: Nome do jogador 8.
      - name: jogador9
        in: formData
        type: string
        required: false
        description: Nome do jogador 9.
      - name: jogador10
        in: formData
        type: string
        required: false
        description: Nome do jogador 10.
    responses:
      200:
        description: Partida registrada com sucesso.
      400:
        description: Faltam informações obrigatórias ou a data é inválida.
      302:
        description: Redireciona para a página principal após registrar a partida.
    """
    boardgame_id = request.form.get('boardgame_id')
    data_partida = request.form.get('data_partida')
    vencedor = request.form.get('vencedor')
    jogadores = {key: value for key, value in request.form.items() if key.startswith('jogador') and value}

    if not boardgame_id or not vencedor or not data_partida:
        return "Faltam informações obrigatórias", 400

    try:
        data_partida = datetime.strptime(data_partida, '%Y-%m-%d').date()
    except ValueError:
        return "Data inválida", 400

    partida = Partidas(
        boardgame_id=boardgame_id,
        data_partida=data_partida,
        jogador1=jogadores.get('jogador1'),
        jogador2=jogadores.get('jogador2'),
        jogador3=jogadores.get('jogador3'),
        jogador4=jogadores.get('jogador4'),
        jogador5=jogadores.get('jogador5'),
        jogador6=jogadores.get('jogador6'),
        jogador7=jogadores.get('jogador7'),
        jogador8=jogadores.get('jogador8'),
        jogador9=jogadores.get('jogador9'),
        jogador10=jogadores.get('jogador10'),
        vencedor=vencedor
    )
    
    db.session.add(partida)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/list_matches', methods=['GET'])
def list_matches():
    """
    Listar todas as Partidas.
    ---
    responses:
      200:
        description: Uma lista de todas as partidas.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: O ID e Primary Key da partida.
              boardgame_name:
                type: string
                description: O nome do Boardgame associado.
              data_partida:
                type: string
                format: date
                description: A data da partida.
              jogadores:
                type: array
                items:
                  type: string
                description: Lista dos jogadores.
              vencedor:
                type: string
                description: O nome do vencedor da partida.
    """
    partidas = db.session.query(Partidas, Boardgames).join(Boardgames, Partidas.boardgame_id == Boardgames.id).all()
    partidas_list = []

    for partida, boardgame in partidas:
        jogadores = [partida.jogador1, partida.jogador2, partida.jogador3, partida.jogador4, partida.jogador5,
                     partida.jogador6, partida.jogador7, partida.jogador8, partida.jogador9, partida.jogador10]
        jogadores = [jogador for jogador in jogadores if jogador]

        partida_data = {
            'id': partida.id,
            'boardgame_name': boardgame.nome,
            'data_partida': partida.data_partida.strftime('%Y-%m-%d'),
            'jogadores': jogadores,
            'vencedor': partida.vencedor
        }
        partidas_list.append(partida_data)

    if not partidas_list:
        return "Não existem partidas cadastradas", 200

    return jsonify(partidas_list)

@app.route('/matches/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    """
    Excluir uma partida pelo ID.
    ---
    parameters:
      - name: match_id
        in: path
        type: integer
        required: true
        description: O ID da partida para ser deletada.
    responses:
      200:
        description: Partida deletada com sucesso.
      404:
        description: Partida não encontrada.
    """
    match_to_delete = Partidas.query.get_or_404(match_id)
    db.session.delete(match_to_delete)
    db.session.commit()
    return jsonify({'message': 'Partida deletada com sucesso'})


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
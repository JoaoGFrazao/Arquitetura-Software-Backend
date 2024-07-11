from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, ForeignKey

db = SQLAlchemy()

class Boardgames(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), nullable=False)
    playerage = db.Column(db.Integer, nullable=False)
    playtime = db.Column(db.Integer, nullable=False)
    min_players = db.Column(db.Integer, nullable=False)
    max_players = db.Column(db.Integer, nullable=False)
    ano_publi = db.Column(db.Integer, nullable=True)

    __table_args__ = (CheckConstraint('min_players <= max_players', name='min_max_player_invalido'),
                      CheckConstraint('playtime > 0', name='invalid_playtime'))

    def __init__(self, nome, playerage, playtime, min_players, max_players, ano_publi):
        self.nome = nome
        self.playerage = playerage
        self.playtime = playtime
        self.min_players = min_players
        self.max_players = max_players
        self.ano_publi = ano_publi

class Partidas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    boardgame_id = db.Column(db.Integer, ForeignKey('boardgames.id'), nullable=False)
    data_partida = db.Column(db.Date, nullable=False)
    jogador1 = db.Column(db.String(20), nullable=False)
    jogador2 = db.Column(db.String(20), nullable=True)
    jogador3 = db.Column(db.String(20), nullable=True)
    jogador4 = db.Column(db.String(20), nullable=True)
    jogador5 = db.Column(db.String(20), nullable=True)
    jogador6 = db.Column(db.String(20), nullable=True)
    jogador7 = db.Column(db.String(20), nullable=True)
    jogador8 = db.Column(db.String(20), nullable=True)
    jogador9 = db.Column(db.String(20), nullable=True)
    jogador10 = db.Column(db.String(20), nullable=True)
    vencedor = db.Column(db.String(20), nullable=False)


    def __init__(self, boardgame_id, data_partida, jogador1, vencedor, jogador2=None, jogador3=None, jogador4=None, jogador5=None, jogador6=None, jogador7=None, jogador8=None, jogador9=None, jogador10=None):
        self.boardgame_id = boardgame_id
        self.data_partida = data_partida
        self.jogador1 = jogador1
        self.jogador2 = jogador2
        self.jogador3 = jogador3
        self.jogador4 = jogador4
        self.jogador5 = jogador5
        self.jogador6 = jogador6
        self.jogador7 = jogador7
        self.jogador8 = jogador8
        self.jogador9 = jogador9
        self.jogador10 = jogador10
        self.vencedor = vencedor
from flask import Flask
from flask_restful import Api

from data.team import Team
from data.player import Player
from data.map import Map
from data.match import Match

app = Flask(__name__)
api = Api(app)

api.add_resource(Team, '/team')
api.add_resource(Player, '/player')
api.add_resource(Map, '/map')
api.add_resource(Match, '/match')

if __name__ == "__main__":
    app.run()
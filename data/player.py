from flask_restful import reqparse


def get_player_data(username: str): pass


class Player:

    argument_dict: dict = {
        "username": True,  # String, user name
        "champion": False,  # list of number, champion id, default all
        "position": False,  # list of number, in game position, default all
        "game_count": False,  # Number, number of game to retrieve, default 100
        "from_game_count": False,  # Number, game on which to start game count, default 0
        "from_date": False,  # Number, timestamp of when to start retrieving, default now
        "to_date": False,  # Number, timestamp of when to stop retrieving, default 0
        "teammates": False,  # List of string, all usernames in user team, default none
        "opponents": False  # List of string, all username in enemy team, default none
    }

    def post(self):
        parser = reqparse.RequestParser()

        for argument in self.argument_dict:
            parser.add_argument(argument, required=self.argument_dict[argument])

        args = parser.parse_args()
        get_player_data(args)

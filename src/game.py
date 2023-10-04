import json

from src.players.ai import AIPlayer
from src.conversation_controller import ConversationController
from src.players.human import HumanPlayer
from src.players.general_dm import DungeonMaster


class Game():

    def __init__(self):
        with open('./src/game_config.json') as json_file:
            self.game_config = json.load(json_file)

        self.players = []
        self.__create_players()
        self.cc = ConversationController(self.players)
        self.dm = DungeonMaster(self.players, self.game_config['dm']['campaign'])


    def __create_players(self):
        for player in self.game_config['players']:
            if player['type'] == 'AI':
                self.players.append(AIPlayer(player))
            elif player['type'] == 'Human':
                self.players.append(HumanPlayer(player))
            else:
                raise Exception("Invalid player type")
            
        # Update each player with the list of other players
        for player in self.players:
            player.set_other_players(self.players)


    def __add_message_to_all(self, message):
        for player in self.players:
            player.add_to_conversation(message)
        self.dm.add_to_conversation(message)
        self.cc.add_to_conversation(message)


    def __call_player(self, name):
        made_call = False
        response = ""
        if name == "Dungeon Master":
            made_call = True
            response = self.dm.get_response()
            self.__add_message_to_all({"role": "user", "name": "dungeon_master", "content": response})
        else:
            for player in self.players:
                if player.name == name:
                    made_call = True
                    response = player.get_response()
                    self.__add_message_to_all({"role": "user", "name": player.name.lower().replace(" ", "_"), "content": response})
                    break

        if not made_call:
            return "Invalid player name"
        else:
            return response


    def start(self):
        dm_begin = self.dm.get_response(begin_campaign=True)
        print(dm_begin)
        self.__add_message_to_all({"role": "user", "name": "dungeon_master", "content": dm_begin})

        while 1 == 1:
            next_player = self.cc.get_next_user()
            response = self.__call_player(next_player)
            if response == "exit":
                break
            print(next_player)
            print(response, "\n\n")


if __name__ == "__main__":
    game = Game()
    print(game.game_config)
        
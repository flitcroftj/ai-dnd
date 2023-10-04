from src.players.player import Player
from IPython.display import clear_output


class HumanPlayer(Player):

    def __init__(self, config: dict):
        super().__init__(config)


    def get_response(self):
        response = input(f"{self.name}: ")
        return response
    
    
    def add_to_conversation(self, statement):
        super().add_to_conversation(statement)
        super().save_conversation(self.name)
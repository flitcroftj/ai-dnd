from abc import ABC, abstractmethod
from src.players.conversation_history import ConversationHistory


class Player(ABC, ConversationHistory):

    def __init__(self, config: dict):
        ConversationHistory.__init__(self)
        self.name = config['name']
        self.player_class = config['player_class']
        self.race = config['race']
        self.level = config['level']
        self.background = config['background']
        self.alignment = config['alignment']
        self.size = config['size']
        self.faith = config['faith']
        self.age = config['age']
        self.personality_traits = config['personality_traits']
        self.flaws = config['flaws']
        self.description = config['description']
        self.type = config['type']
        self.other_players = []


    @abstractmethod
    def get_response(self):
        pass
    

    def get_character_description(self):
        return self.description
    

    def set_other_players(self, players):
        # Exclude self from the players list
        self.other_players = [p for p in players if p is not self]
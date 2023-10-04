import os
import openai
from abc import ABC
from src.players.conversation_history import ConversationHistory

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

openai.api_key = os.getenv('OPENAI_API_KEY')


class DungeonMaster(ABC, ConversationHistory):

    def __init__(self, players, campaign: str):
        ConversationHistory.__init__(self)
        self.campaign = campaign
        self.players = players
        self.system_message = self.__generate_system_message()
    

    def __generate_campaign_start_message(self):
        return {"role": "user", "content": "Please introduce the campaign and the setting. Then ask one of the players to begin."}


    def __generate_system_message(self):
        message =  f"You are a dungeon master running a DND a campaign based around {self.campaign}. There are {len(self.players)} players in the campaign, some are played by an AI like you, some played by a Human. Here is a bit about them:\n"
        for player in self.players:
            message += f"Name: {player.name}, Class: {player.player_class}, Race: {player.race}, a bit about them: {player.description}\n. This player is controlled by a(n) {player.type}."
        message += f"Keep responses around 50 words max if possible to not dominate the game, except when describing a setting. Try to interact more with the human players over the AI ones. Only respond as the dungeon master when you are speaking. Absolutely never make up a response from a player, only respond as the dungeon master."
        return {"role": "system", "content": message}


    def get_response(self, begin_campaign=False) -> str:
        if begin_campaign:
            messages = [self.system_message] + [self.__generate_campaign_start_message()] + self.conversation
        else:
            messages = [self.system_message] + self.conversation
        
        for message in messages:
            message['content'] = message['content']

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            # functions=FUNCTIONS,
            # function_call='auto',
            temperature=1,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        self.conversation_response_data.append(response)
        return response["choices"][0]["message"]["content"]


    def add_to_conversation(self, statement):
        self.add_to_conversation_ai(statement, name="DM")
import os
import openai

from src.players.player import Player
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

openai.api_key = os.getenv('OPENAI_API_KEY')


class AIPlayer(Player):

    def __init__(self, config: dict):
        super().__init__(config)
        self.system_message = self.__generate_system_message()


    def __generate_system_message(self):
        message =  f"You are an AI playing Dungeons and Dragons. You are {self.name}, a level {self.level} {self.race} {self.player_class}. Here is a description of your character: {self.description}"
        message += f"You are {self.age} years old, your size is {self.size}, your alignment is {self.alignment}, your background is {self.background}. Your strengths are {self.personality_traits}, your faith is {self.faith}, and your flaws are {self.flaws}."
        message += f"You are playing with {len(self.other_players)} other player(s). Here is a bit about them:\n"
        for player in self.other_players:
            message += f"Name: {player.name}, {player.description}\n. This player is controlled by a(n) {player.type}."
        message += f"Keep responses around 50 words max if possible to not dominate the game. Only respond as {self.name} when you are speaking. You may recognize the campaign, but you are not allowed to use any knowledge of the campaign to inform your responses."
        return {"role": "system", "content": message}


    def get_response(self) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[self.system_message] + self.conversation,
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
        super().add_to_conversation_ai(statement, self.name)
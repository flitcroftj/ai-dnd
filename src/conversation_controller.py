import os
import openai
import json
from abc import ABC
from src.players.conversation_history import ConversationHistory

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

openai.api_key = os.getenv('OPENAI_API_KEY')


class ConversationController(ABC, ConversationHistory):

    def __init__(self, players):
        ConversationHistory.__init__(self)
        self.players = players
        self.player_names = [player.name for player in self.players]
        self.system_message = self.__generate_sys_message()
        self.function_calls = self.__generate_function_calls()
        self.num_calls = 0
        self.num_input_tokens = 0
        self.num_output_tokens = 0
        self.player_calls = {player.name: 0 for player in self.players}
        self.player_calls["Dungeon Master"] = 0


    def __generate_sys_message(self):
        message = "You are moderating a DND campaign and are to select which player should speak next based on the conversation. If a player is asking a question about the game, call the Dungeon Master."
        human_players = [player for player in self.players if player.type == "Human"]
        message += f"Bias yourself towards calling on the human players, who are: {', '.join([player.name for player in human_players])}"
        message += "Don't call on the same player twice in a row."

        return {"role": "system", "content": message}
    

    def __generate_function_calls(self):
        return [
            {
                "name": "get_person_input",
                "description": "Request the next person to give input",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "person": {
                            "type": "string",
                            "enum": self.player_names + ["Dungeon Master"],
                            "description": "The name of the person to request input from"
                        }
                    },
                    "required": ["person"]
                },
            }
        ]

    
    def __get_last_three_messages(self):
        return self.conversation[-3:]


    def get_next_user(self):
        if len(self.conversation) == 0:
            return "DM"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[self.system_message] + self.__get_last_three_messages(),
            functions=self.function_calls,
            function_call={"name": "get_person_input"},
            temperature=0.05,
            max_tokens=200,
            top_p=0.9,
            frequency_penalty=0,
            presence_penalty=0
        )
        self.num_calls += 1
        self.num_input_tokens += response["usage"]["prompt_tokens"]
        self.num_output_tokens += response["usage"]["completion_tokens"]
        choice = json.loads(response["choices"][0]["message"]["function_call"]["arguments"])["person"]
        self.player_calls[choice] += 1
        return choice
    

    def write_stats(self, file_path):
        with open(file_path, 'w') as f:
            json.dump({
                "conversation_controller": {
                    "num_calls": self.num_calls,
                    "num_input_tokens": self.num_input_tokens,
                    "num_output_tokens": self.num_output_tokens,
                    "player_calls": self.player_calls
                }
            }, f)
import os
import openai
import json
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

openai.api_key = os.getenv('OPENAI_API_KEY')


class ConversationHistory():

    def __init__(self):
        self.conversation = []
        self.conversation_response_data = []
        self.summary_response_data = []
        self.summarize_at = 7
        self.num_messages_to_keep = 4


    def __get_conversation_to_summarize(self):
        to_summarize = self.conversation[:-self.num_messages_to_keep]
        conversation = "This is the conversation to summarize:\n"
        for message in to_summarize:
            conversation += "Speaker: " + message['name'] + "\n"
            conversation += "Statement: " + message['content'] + "\n"
        return [{'role': 'user', 'content': conversation}]
    

    def save_conversation(self, name):
        # First delete the old file
        with open("src/game_data/" + name + "_conversation.txt", "w") as f:
            pass
        with open("src/game_data/" + name + "_conversation.txt", "a") as f:
            f.write("--------------------\n")
            for i, statement in enumerate(self.conversation):
                f.write("Statement " + str(i) + "\n\n" + statement["name"] + ':\n' + statement["content"] + "\n")
                f.write("--------------------\n\n")

    
    def add_to_conversation(self, statement):
        self.conversation.append(statement)


    def add_to_conversation_ai(self, statement, name):
        self.conversation.append(statement)
        self.summarize_conversation()
        self.save_conversation(name)
        with open("src/game_data/" + name + "_metadata.txt", "w") as f:
            for response in self.conversation_response_data:
                f.write(json.dumps(response) + "\n\n\n")
    

    def get_latest_response(self):
        return self.conversation[-1]
    

    def get_conversation(self):
        return self.conversation
    

    def summarize_conversation(self):
        # Has to be greater than 7 cause when the summary gets added it will be 8, but 7 of the previous messages will be there
        if len(self.conversation) > self.summarize_at:
            messages = [{"role": "system", "content": "You are monitoring a DND game for AI players. You are to take their conversation and previous summary, and summarize it into less than 200 words that describes the setting and what has happened. Keep it as concise as possible."}]
            messages += self.__get_conversation_to_summarize()
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=1,
                max_tokens=700,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            response['prompt'] = messages
            self.summary_response_data.append(response)
            summary = response["choices"][0]["message"]["content"]
            self.conversation = self.conversation[-self.num_messages_to_keep:]
            self.conversation.insert(0, {"role": "user", "name": "summary", "content": "Summary of previous activities: " + summary})
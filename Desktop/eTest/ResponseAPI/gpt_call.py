import openai
import re

openai.api_key = "ac613c4824814a468b2b0d7a1a254f3f"
openai.api_base = "https://rupaopenai.openai.azure.com/" 
openai.api_type = 'azure'
openai.api_version = '2023-05-15'  
deployment_name = 'gpt35turbo' 

def truncate_text(text, max_tokens):
        # Remove unnecessary white spaces and underscores
        text = re.sub(r'\s+', '', text)
        text = re.sub(r'_+', '', text)
        text = re.sub(r'-+', '', text)
        text = re.sub(r'\n+', '', text)


        tokens = text.split()
        if len(tokens) <= max_tokens:
            return text

        return ' '.join(tokens[:max_tokens])
        
def chat_gpt(prompt, model="gpt-35-turbo", max_tokens=1024, max_context_tokens=4000, safety_margin=5):
        print("blah blah ")
        # Truncate the prompt content to fit within the model's context length
        truncated_prompt = truncate_text(prompt, max_context_tokens - max_tokens - safety_margin)
        message = messages = [{"role": "user", "content": truncated_prompt}]

        response = openai.ChatCompletion.create(engine=deployment_name, model=model, 
                                           temperature=0, max_tokens=800,messages=message)

        return response["choices"][0]["message"]["content"]
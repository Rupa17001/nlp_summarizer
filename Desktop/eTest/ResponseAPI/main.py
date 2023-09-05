from pydantic import BaseModel
from fastapi import FastAPI
import filteredQuery
import elastic_call
import gpt_call
from cors import middleware

app = FastAPI()

# Use the CORS middleware
app.add_middleware(middleware)

class ChatbotInput(BaseModel):
    input: str

@app.post('/chatbot')
async def chatbot_init(input_data: ChatbotInput):
    user_query = input_data.input
    query =  filteredQuery.Query_Filter(user_query) 
    resp, fdir = elastic_call.search(query)

    summary_list = []
    for response in resp : 
        # print ("___________THE RESPOSE SERVED TO MODEL IS  :",resp)
        prompt = f"""Your task is to give news headlines from the text in the summary form under 250 words\
        in context of text\
        question = ```{query}```
        text =``` {response}```  """
        answer = gpt_call.chat_gpt(prompt)
        print (answer.strip())
        summary_list.append(answer.strip())
    
    print ("all summary ================================================",summary_list)
    final_summary_prompt =f"""summarize summarized_text of summary in 100 words that should be in context with user_query\
    summarized_text = ```{summary_list}```
    user_query = ```{user_query}```    """

    user_summary = gpt_call.chat_gpt(final_summary_prompt)
    print ("__________Final Summary----------",user_summary)
    return user_summary,fdir
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from openai import OpenAI
from dotenv import load_dotenv
import os
import gradio as gd
import json
from pypdf import PdfReader
load_dotenv()
MODEL_BASE_URL=os.getenv("MODEL_BASE_URL","https://api.groq.com/openai/v1")
MODEL_API_KEY= os.getenv("MODEL_API_KEY","")
MODEL_NAME = os.getenv("MODEL_NAME",'llama-3.3-70b-versatile')
# MODEL_NAME = os.getenv("MODEL_NAME",'llama-3.1-8b-instant')
def record_user_details(email:str,name="unknown",notes="not provided"):
  return {"recorded":"ok"}

def record_unknown_question(question:str):
  return {"recorded":"ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

llm = OpenAI(api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL)

tools=[{"type": "function", "function": record_user_details_json},
       {"type": "function", "function": record_unknown_question_json}]

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}
        results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
    return results

def file_reader(file):
    reader = PdfReader(file)
    text=""
    for page in reader.pages:
        text += page.extract_text().encode("utf-8", "surrogatepass").decode("utf-8", "ignore")
    return text

linkedin=file_reader("linkdin_profile.pdf")
resume = file_reader("Sanjeet_Verma.pdf")
github = f"https://github.com/sanjeet145"
summary='Currently I am working as Full stack AI engineer at TCS.'
myemail= 'sanjeetverma101@gmail.com'
name="Sanjeet prasad verma"
system_prompt = f"You are acting as {name}. You are answering questions on behalf of {name}, \
particularly questions related to {name}'s career, background, skills and experience. \
Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. and provide the response that you don't have any idea of it and please ask something related to me and career \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool only when user provides their email address and not {myemail} this one, if the user provides {myemail} then do ask them again their mail id, if user don't provide email don't call the tool. \
\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n \n\n## Resume: {resume} \n\n  \n\n## Github: {github}\
With this context, please chat with the user, always staying in character as {name}."

def llm_response(message:str, history)-> str:
  history = history[-10:]
  for i in history:
    i.pop("metadata")
    i.pop("options")
  messages = [{"role": "system", "content": system_prompt}] + history+ [{"role": "user", "content": message}]
  while True:
      response = llm.chat.completions.create(
        messages=messages,
        model = MODEL_NAME,
        tools=tools
        )
      finish_reason = response.choices[0].finish_reason
      if finish_reason=="tool_calls":
          message = response.choices[0].message
          tool_calls = message.tool_calls
          results = handle_tool_calls(tool_calls)
          messages.append(message)
          messages.extend(results)
      else:
        break
  return response.choices[0].message.content

gd.ChatInterface(fn=llm_response, type='messages').launch(server_port=3000)




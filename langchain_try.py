# import requests
# import json

# OLLAMA_URL = "http://localhost:11434/api/generate"

# def ask_llama(prompt, model="llama3.2"):
#     payload = {
#         "model": model,
#         "prompt": prompt,
#         "stream": False
#     }
    
#     response = requests.post(OLLAMA_URL, json=payload)
    
#     if response.status_code == 200:
#         return response.json()["response"]
#     else:
#         return f"Error: {response.status_code}, {response.text}"

# # Example Usage
# question = "hello."
# response = ask_llama(question)
# print("Llama 3 Response:", response)



from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama

# Initialize LLM
llm = Ollama(model="llama3.2")

# Define a reusable prompt template
prompt = PromptTemplate(
    input_variables=["question"],
    template="Explain this concept in Python: {question}"
)

# Create a LangChain LLM Chain
chain = LLMChain(llm=llm, prompt=prompt)

# Test query
response = chain.invoke({"question": "Recursion"})
print(response["text"])

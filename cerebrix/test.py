from aimodels.models import ChatModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages.utils import trim_messages

# chat_model = ChatModel.objects.get(code="ollama_llama3.1")
# print('Tokens: ', chat_model.count_tokens('test lorem ipsum dolor sit amet'))

# llama3_1 = ChatModel.objects.get(code="ollama_llama3.1").model
# print('Tokens: ', llama3_1.get_num_tokens('test lorem ipsum dolor sit amet'))

# template = ChatPromptTemplate([
#     ("system", "You are a helpful assistant."),
#     MessagesPlaceholder(variable_name="history"),
#     ("human", "{user_input}"),
# ])

# history = [
#     HumanMessage(content="How are you?"),
#     AIMessage(content="I'm doing well, thanks!"), 
#     HumanMessage(content="What is the capital of France?"),
#     AIMessage(content="The capital of France is Paris."),
#     HumanMessage(content="Do you know the capital of Spain?"),
#     AIMessage(content="The capital of Spain is Madrid."),
# ]

# runnable = template | llama3_1

# resp = runnable.invoke({"user_input": "Can you write a python function that returns the sum of two numbers?", "history": history})

# print(resp.content)



# messages = [SystemMessage(content="You are a helpful assistant."), HumanMessage(content="How are you?")]
# resp = llama3_1.invoke(messages)

# print(messages[0].type)
# print(messages[1].type)


from threads.services import ThreadService
from threads.models import Thread, ThreadMessage

thread = Thread.objects.get(id=1)
service = ThreadService(thread)
if thread.messages.count() == 0:
    service.initialize()

resp = service.send_message("Hello, how are you?")
print(resp.content_value)
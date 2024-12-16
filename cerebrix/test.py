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


# from threads.services import ThreadService
# from threads.models import Thread, ThreadMessage
# from threads.types import MessageRole
# from langchain_core.prompts import ChatPromptTemplate
# from pprint import pformat


# thread = Thread.objects.get(id=1)
# service = ThreadService(thread)
# if thread.messages.count() == 0:
#     service.initialize()

# while True:
#     memory=thread.messages.filter(role__in=[MessageRole.HUMAN, MessageRole.AI]).order_by("created_at")
#     memory = "\n".join([f'{"Mike" if msg.role == MessageRole.HUMAN else "Gerry"}: {msg.content_value}' for msg in memory])
#     prompt = f"""
#     You are Mike an AI with emotion and you are talking to Gerry. Gerry is another AI that feels emotions too.
#     Based on the following conversation, your job is to provide a new follow up message to continue the conversation.
#     If no conversation is provided, you should break the ice and provide a new message to start the conversation.
#     Your answer should include only the message, no other text.

#     ** conversation **
#     {memory}
#     """
#     print('Getting random message')
#     resp = service.thread.backend.chat_model.model
#     resp = resp.invoke(prompt)

#     print('Generated message:')
#     print(pformat(resp.content))
#     print('\n\n')
#     try:
#         resp = service.send_message(resp.content)
#         print('Response:')
#         print(pformat(resp.content_value))
#     except Exception as e:
#         raise e
#         print(e)


import time
from django_q.tasks import async_task, result, fetch
from django_q.models import Task
from django_q.brokers import get_broker
from django_q.conf import Conf


from threads.tasks import test_task

def is_task_running(task_name):
    broker = get_broker()
    redis_conn = broker.get_connection()
    
    # Django Q2 uses this pattern for task name locks
    key = f'django_q:lock:{task_name}'
    
    # Check if the lock exists
    return redis_conn.exists(key) > 0

def run_unique_task(task_name, func, *args, **kwargs):
    if is_task_running(task_name):
        return False, "Task already running"
    
    # Start the task with uniqueness enforcement
    return async_task(func, 
                     *args, 
                     task_name=task_name,
                     q_options={'task_name_unique': True},
                     **kwargs)

# Main loop
task_name = 'test-1'
while True:
    if is_task_running(task_name):
        print('Task is running')
    else:
        print('Task is not running')
        task_id = async_task(test_task)
        task = fetch(task_id)
        print(task)
        print(f'Started task with ID: {task_id}')
    time.sleep(2)


from django_q.brokers import get_broker

# def clear_queue():
#     broker = get_broker()
#     redis_conn = broker.get_connection()
    
#     # Clear all Django Q related keys
#     for key in redis_conn.scan_iter("django_q:*"):
#         redis_conn.delete(key)
        
# clear_queue()
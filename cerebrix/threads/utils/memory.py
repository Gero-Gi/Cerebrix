from typing import List, Tuple
import logging
from django.db.models.functions import Coalesce

 
from django.db.models import Sum
from langchain.schema import BaseMessage

from threads.models import Thread
from threads.models import MessageRole

from threads.tasks import update_memory_summary
from common.utils.tasks import is_task_running


logger = logging.getLogger("threads.utils.memory")


def get_basic_memory(thread: Thread) -> Tuple[List[BaseMessage], int]:
    """
    Return the last messages in the thread, starting from the first human message
    The messages will be truncated if the memory size is exceeded.
    """
    messages = thread.messages.filter(role__in=[MessageRole.HUMAN, MessageRole.AI]).order_by("created_at")
    tokens = 0
    history = []
    for message in messages:
        tokens += message.content_tokens
        history.append(message.get_message())
        if (
            tokens >= thread.backend.memory_size_tokens
            and message.role == MessageRole.HUMAN
        ):
            break
    return history, tokens


def get_simple_memory(
    thread: Thread, threshold: int = 10
) -> Tuple[List[BaseMessage], int]:
    """
    Return memory composed of two elements:
    - short term memory: latest messages in the thread
    - long term memory: summary of older messages
    The short term memory will contain at least backend.short_term_memory_size messages

    When the size of the memory exceeds the backend.context_window - `threshold`, another summary is created asynchronously
    with the oldest messages and the previous summary.
    Since the creation of the summary is asynchronous, a mechanism is used to avoid race conditions (also why a threshold is used).

    NOTE: to guarantee a robust memory, it is not guaranteed that the memory size does not exceed the backend.memory_size
        still the backend.memory_size is taken into account to build the memory

    Args:
        threshold (int): the threshold in percentage of the context window to create a new summary
    """
    # print('get_simple_memory', thread.id)
    # logger.debug('get_simple_memory', thread.id)
    last_summary = thread.messages.filter(role=MessageRole.SUMMARIZER).order_by(
        "-created_at"
    )
    last_messages = thread.messages.filter(
        role__in=[MessageRole.HUMAN, MessageRole.AI]
    ).order_by("created_at")
    if last_summary.exists():
        last_summary = last_summary.first()
        last_summary_tokens = last_summary.content_tokens
        # only the messages after the last summary are considered
        last_messages = last_messages.filter(created_at__gt=last_summary.created_at)
    else:
        last_summary = None
        last_summary_tokens = 0

    total_tokens = (
        last_summary_tokens
        + (last_messages.aggregate(Sum("content_tokens"))["content_tokens__sum"]
        or 0)
    )

    threshold = thread.backend.memory_size_tokens * threshold / 100

    if total_tokens > thread.backend.memory_size_tokens - threshold:
        logger.debug("Generating summary")
         # make sure that a task with the same id is not running, if it is don't run this one
        task_id = f"thread.memory.summary.{thread.id}"
        if is_task_running(task_id):
            logger.debug("Summary task already running")
        else:
            logger.debug("Generating new summary")
            update_memory_summary.apply_async(
                args=[thread.id, last_messages.last().id], task_id=task_id
            )

    memory = []
    if last_summary:
        memory.append(last_summary.get_message())
    memory.extend([msg.get_message() for msg in last_messages.order_by("created_at")])

    return memory, total_tokens

import logging
from datetime import timedelta
from time import sleep
 
from langchain_core.prompts import ChatPromptTemplate
from threads.models import Thread, ThreadMessage
from threads.prompts import THREAD_SUMMARY_PROMPT
from threads.types import MessageRole

from common.utils import get_input_tokens, get_output_tokens
from common.utils.tasks import locked_task

logger = logging.getLogger("threads.tasks")
 

def update_memory_summary(thread_id: int, thread_message_id: int):
    """
    Updates the memory summary for a thread by summarizing older messages.

    This task:
    1. Retrieves messages between the last summary and a given message
    2. If there are enough messages beyond short-term memory size, creates a new summary
    3. Uses LLM to generate a summary of older messages, incorporating previous summary if it exists
    4. Helps manage context window by condensing older messages into a summary

    Args:
        thread_id (int): ID of the thread to update summary for
        thread_message_id (int): ID of the message that triggered the summary update
    """
    sleep(60)
    logger.debug(f"Updating memory summary for thread {thread_id}")
    thread_message = ThreadMessage.objects.get(id=thread_message_id)
    thread = Thread.objects.get(id=thread_id)

    filters = {
        "thread_id": thread_id,
        "created_at__lt": thread_message.created_at,
        "role__in": [MessageRole.HUMAN, MessageRole.AI],
    }
    last_summary = ThreadMessage.objects.filter(
        thread_id=thread_id, role=MessageRole.SUMMARIZER
    ).order_by("-created_at")
    
    if last_summary.exists():
        last_summary = last_summary.first()
        logger.debug(f"Last summary: {last_summary.content_value}")
        filters["created_at__gt"] = last_summary.created_at
    else:
        last_summary = None

    # messages in between the last summary and the current message
    messages = ThreadMessage.objects.filter(**filters).order_by("-created_at")
    # make sure that enaugh messages are available for short term memory
    if messages.count() <= thread.backend.short_term_memory_size:
        logger.debug("Not enough messages to summarize")
        return

    # get all messages to summarize -> messages in between the last summary and the first message
    # to be included in the short term memory
    first_short_term_memory_message = messages[
        thread.backend.short_term_memory_size - 1
    ]
    to_summarize_qs = messages.filter(
        created_at__lt=first_short_term_memory_message.created_at
    ).order_by("created_at")
    to_summarize = "\n".join(
        [f"{m.get_role_display()}: {m.content_value}" for m in to_summarize_qs]
    )

    # create a new summary
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", THREAD_SUMMARY_PROMPT),
        ]
    )
    chain = chat_prompt | thread.backend.chat_model.get_model()
    # logger.debug(chat_prompt.format_messages(messages=to_summarize, previous_summary=last_summary.content_value if last_summary else None))
    try:
        resp = chain.invoke(
            {
                "messages": to_summarize,
                "previous_summary": (
                    last_summary.content_value if last_summary else None
                ),
            }
        )
        logger.debug(f"Summary: {resp}")
    except Exception as e:
        logger.error(f"Error summarizing thread: {e}")
        return

    # get the actual tokens spent to generate the summary
    spent_tokens = get_output_tokens(resp) + get_input_tokens(resp)

    summary = f"""
    Please answer any follow-up questions based on your original purpose, 
    using the following summary of past messages as context:
    {resp.content}
    """

    # add the new summary a millisecond after the last summarized message
    ThreadMessage.objects.create(
        thread_id=thread_id,
        created_at=to_summarize_qs.last().created_at + timedelta(milliseconds=1),
        content=summary,
        total_tokens=spent_tokens,  # this is the total number of tokens spent to generate the summary
        content_tokens=thread.backend.chat_model.count_tokens(summary),
        role=MessageRole.SUMMARIZER,
    )

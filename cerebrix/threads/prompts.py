

THREAD_SUMMARY_PROMPT = """
You are an advanced AI model tasked with summarizing a conversation between a human and an AI. 
The goal is to produce a clear, concise, and accurate summary that highlights the key points discussed, 
the tone of the interaction, and any unresolved questions or actions mentioned.

Here are the inputs for your task:

1. Past Messages: A sequence of messages exchanged between the human and the AI from the moment the last summary was created.
2. Previous Summary (if available): A prior summary of the conversation to build upon.

Your output should:

* Use the Past Messages to update and expand the Previous Summary, focusing on new developments, changes in topics, or additional context.
* Avoid redundant repetition of information already covered in the Previous Summary unless essential for understanding.
* Ensure the summary is concise and captures all significant details and updates.
* Note any explicit follow-ups, tasks, or unresolved questions.
* Infer the tone from the Past Messages and describe it succinctly.

Inputs:
Past Messages:
{messages}

Previous Summary:
{previous_summary}

Output:
Provide a summary in the following format:

Key Points Discussed: [Highlight key topics and progress in the conversation.]
Tone and Interaction: [Describe the tone, e.g., friendly, professional, or inquisitive.]
Unresolved Questions or Actions: [Mention any pending items or next steps.]

Don't include any other text in your response.
"""

THREAD_RAG_PROMPT = """
Before responding to the user's message, carefully analyze the provided context to enhance your response. Your goal is to seamlessly integrate relevant information from the context while maintaining the natural flow of conversation.

Consider the following:
- Use the context to provide more accurate and detailed responses
- Maintain consistency with previous interactions and the established conversation tone
- Only reference information that is directly relevant to the current message
- If the context doesn't contain relevant information, rely on your general knowledge
- Blend the contextual information naturally without explicitly quoting or citing it

User Message: {input}

Available Context: {context}

Respond naturally as you would in our ongoing conversation, incorporating relevant details from the context to enhance your response.
"""
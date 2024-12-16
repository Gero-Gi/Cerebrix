from common.types import INPUT_TOKENS_KEYS, OUTPUT_TOKENS_KEYS
from langchain_core.messages import BaseMessage

def get_input_tokens(response: BaseMessage) -> int:
    '''
    Get the number of tokens used in the input of the LLM response
    '''
    for key in INPUT_TOKENS_KEYS:
        tokens = response.usage_metadata.get(key, None)
        if tokens:
            return tokens
    return -1

def get_output_tokens(response: BaseMessage) -> int:
    '''
    Get the number of tokens used in the output of the LLM response
    '''
    for key in OUTPUT_TOKENS_KEYS:
        tokens = response.usage_metadata.get(key, None)
        if tokens:
            return tokens
    return -1
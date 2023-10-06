from enum import Enum

class Actions(Enum):
    ANTIPATTERN = 'Antipattern'
    ADD_EXCEPTION_TO_TOKEN = 'Add exception to token'
    CHANGE_FINAL_TOKEN = 'Change final token so it requires one of these words'
    ADD_TOKEN_AT_END = 'Add token at end requiring one of these words'
    CHANGE_SECOND_TOKEN = 'Change second token'
    ADD_TOKENS_BEFORE_AND_AFTER = 'Add tokens before and after'
    EXCLUDE_FROM_INITIAL_TOKEN = 'Exclude from initial token'
    EXCLUDE_FROM_FIRST_TOKEN = 'Exclude from first token'
    ANTIPATTERNS = 'Antipatterns'
    ADD_REQUIRED_TOKENS = 'Add required tokens both before and after the string'
    EXCLUDE_FROM_FINAL_TOKEN = 'Exclude from final token'
    EXCLUDE_FROM_SECOND_TOKEN = 'Exclude from second token'
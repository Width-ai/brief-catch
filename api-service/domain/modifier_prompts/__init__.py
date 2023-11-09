from domain.constants import Modifications
from . import (
    antipattern,
    add_exception_to_token,
    change_final_token,
    add_token_at_end,
    change_second_token,
    add_tokens_before_and_after,
    exclude_from_initial_token,
    exclude_from_first_token,
    antipatterns,
    add_required_tokens,
    exclude_from_final_token,
    exclude_from_second_token
)

# Import this dictionary for the rule modifying system prompts
RULE_MODIFYING_SYSTEM_PROMPTS = {
    Modifications.ANTIPATTERN.value: antipattern.SYSTEM_PROMPT,
    Modifications.ADD_EXCEPTION_TO_TOKEN.value: add_exception_to_token.SYSTEM_PROMPT,
    Modifications.CHANGE_FINAL_TOKEN.value: change_final_token.SYSTEM_PROMPT,
    Modifications.ADD_TOKEN_AT_END.value: add_token_at_end.SYSTEM_PROMPT,
    Modifications.CHANGE_SECOND_TOKEN.value: change_second_token.SYSTEM_PROMPT,
    Modifications.ADD_TOKENS_BEFORE_AND_AFTER.value: add_tokens_before_and_after.SYSTEM_PROMPT,
    Modifications.EXCLUDE_FROM_INITIAL_TOKEN.value: exclude_from_initial_token.SYSTEM_PROMPT,
    Modifications.EXCLUDE_FROM_FIRST_TOKEN.value: exclude_from_first_token.SYSTEM_PROMPT,
    Modifications.ANTIPATTERNS.value: antipatterns.SYSTEM_PROMPT,
    Modifications.ADD_REQUIRED_TOKENS.value: add_required_tokens.SYSTEM_PROMPT,
    Modifications.EXCLUDE_FROM_FINAL_TOKEN.value: exclude_from_final_token.SYSTEM_PROMPT,
    Modifications.EXCLUDE_FROM_SECOND_TOKEN.value: exclude_from_second_token.SYSTEM_PROMPT
}

RULE_USER_TEXT_TEMPLATE = """# Original Rule:
{{origininal_rule_text}}

# Action to take:
{{action_to_take}}

Specific Modifications:
{{list of specific Modifications}}

# Modified Rule:"""

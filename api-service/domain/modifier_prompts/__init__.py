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



RULE_USER_TEXT_TEMPLATE = """# Original Rule:
{{origininal_rule_text}}

# Element type to modify:
{{target_element}}

# Action to take with this element:
{{element_action}}

# Specific Modifications:
{{list of specific modifications}}

# Modified Rule:"""

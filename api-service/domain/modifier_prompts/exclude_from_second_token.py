from domain.modifier_prompts.common_instructions import (
    RULE_TAG_CLEANING, 
    RULE_TAG_CREATION,
    SYMBOL_REPLACEMENT,
    ADD_SHORT_TEMPLATE,
    ELEMENT_ORDER_RULES,
    PATTERN_CLARIFICATION
)

# Exclude from second token
SYSTEM_PROMPT = f"""You will be given a rule, an action to take and specificities around the action in the user text. Modify the original xml rule according to based on the action and following the below instructions:

(1) {RULE_TAG_CLEANING}

(2) {RULE_TAG_CREATION}

(3) {SYMBOL_REPLACEMENT}

(4) {ADD_SHORT_TEMPLATE}

(5) {ELEMENT_ORDER_RULES}

(6) {PATTERN_CLARIFICATION}
"""

USER_EXAMPLE = """
# Original Rule:
BRIEFCATCH_44581927263068961765770112333921380316 
BRIEFCATCH_CONCISENESS_20528 

<pattern>
<token>firmly</token>
<token inflected="yes">establish</token>
</pattern>
<suggestion>
<match no="2"/>
</suggestion>
<message>Would an adverb such as *firmly* be redundant here?</message>
<example correction="established">The theory has been <marker>firmly established</marker>.</example>

# Action to take:
exclude from second token

Specific Actions:
Add an exception for the word "established" to the second token of the pattern. Add it right behind the word "establish" and right before the closing '</token>' tag of that token. Nest the word in between an opening '<exception>' and a closing '</token>' tag.

Modify the existing example correction element so that it accurately reflects the made changes.

# Modified Rule:
"""

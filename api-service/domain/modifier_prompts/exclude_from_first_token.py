from domain.modifier_prompts.common_instructions import (
    INSTRUCTION_INTRO,
    RULE_TAG_CLEANING, 
    RULE_TAG_CREATION,
    SYMBOL_REPLACEMENT,
    ADD_SHORT_TEMPLATE,
    ELEMENT_ORDER_RULES
)

# Exclude from first token
SYSTEM_PROMPT = f"""{INSTRUCTION_INTRO}

# Section 1:
Modify the xml according to the specific Actions

# Section 2:
(1) {RULE_TAG_CLEANING}

(2) {RULE_TAG_CREATION}

(3) {SYMBOL_REPLACEMENT}

(4) {ADD_SHORT_TEMPLATE}

(5) {ELEMENT_ORDER_RULES}
"""

USER_EXAMPLE = """
# Original Rule:
BRIEFCATCH_199521758025408900899326796412516191904BRIEFCATCH_CONCISENESS_5808

<pattern>
<token regexp="yes">judgment|judgement</token>
<token>in</token>
<token>this</token>
<token regexp="yes">case|action|matter</token>
</pattern>
<suggestion>\1</suggestion>
<message>**In this matter** or **judgment** is usually implied when you refer to a particular dispute.|**Example** from Walter Dellinger: ‚Äú[T]he appropriate remedy would be to reverse the **judgment** and remand with instructions directing the district court to engage in appropriate fact-finding.‚Äù|**Example** from Shay Dvoretzky: ‚ÄúEven so, Petitioner claims that he did not know about **the judgment** until September 2014[.]‚Äù</message><example correction="judgment">Sought <marker>judgment in this case</marker>.</example>

# Action to take:
Exclude from first token

Specific Actions:
Delete the word option "case" from the final token of the pattern. Modify the example phrase in the example correction element accordingly so that it reflects the before change and matches the modified pattern.

# Modified Rule:
"""

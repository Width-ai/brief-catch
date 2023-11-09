from domain.modifier_prompts.common_instructions import (
    RULE_TAG_CLEANING, 
    RULE_TAG_CREATION,
    SYMBOL_REPLACEMENT,
    ADD_SHORT_TEMPLATE,
    ELEMENT_ORDER_RULES,
    PATTERN_CLARIFICATION
)

# Exclude from final token
SYSTEM_PROMPT = f"""You will be given a rule, an action to take and specificities around the action in the user text. Modify the xml rule according to the info provided below.

(1) {RULE_TAG_CLEANING}

(2) {RULE_TAG_CREATION}

(3) {SYMBOL_REPLACEMENT}

(4) {ADD_SHORT_TEMPLATE}

(5) {ELEMENT_ORDER_RULES}

(6) {PATTERN_CLARIFICATION}
"""

USER_EXAMPLE = """
# Original Rule:
BRIEFCATCH_109552035637828470607412367173721816662BRIEFCATCH_CONCISENESS_5311
<pattern>
<token>had</token>
<token>already</token>
<token postag="VBN">
<exception regexp="yes">begun|decided|happened|intervened|occurred|started|transpired</exception></token>
</pattern>
<suggestion>had \3</suggestion>
<message>Could cutting this implied adverb help tighten the sentence? The past perfect tense (**I had known** vs. **I knew**) usually makes the **already** redundant.|**Example** from Justice Gorsuch: ‚ÄúCustody pursuant to a final judgment was proof that a defendant **had received** the process due to him.‚Äù|**Example** from Justice Ginsburg: ‚Äú[O]ther shareholders who **had filed** their own class complaints dismissed them[.]‚Äù</message>
 <example correction="had ruled">the trial court <marker>had already ruled</marker> favorably</example>

# Action to take:
exclude from final token

Specific Actions:
Add an exception for the word "been" as an additional regexp option to the exception element under the final token of the pattern, make it the first option.

# Modified Rule:
"""

from domain.modifier_prompts.common_instructions import (
    INSTRUCTION_INTRO,
    RULE_TAG_CLEANING, 
    RULE_TAG_CREATION,
    SYMBOL_REPLACEMENT,
    ADD_SHORT_TEMPLATE,
    ELEMENT_ORDER_RULES
)

# Change second token
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
BRIEFCATCH_23265665707036495693898601905022857498 BRIEFCATCH_PUNCHINESS_778 

<antipattern> 

   <token>further</token> 

   <token regexp="yes">proof|evidence</token> 

   <token regexp="yes">for|of|that</token> 

 </antipattern>  

<pattern> 

   <token>further</token> 

   <token regexp="yes">proof|evidence</token> 

 </pattern> 

 <suggestion>more \2</suggestion> 

 <suggestion>other \2</suggestion> 

 <message>Would shorter words add punch? Would replacing the legalistic word **further** help lighten the style?|**Example** from Justice Scalia: ‚ÄúWere **more proof** needed to show that this is an entitlement program, not a remedial statute, it should . . . .‚Äù|**Example** from Justice Alito: ‚ÄúPost-1952 judicial decisions addressing assignor estoppel supply yet **more evidence** that the status of the doctrine was (at best) uncertain when Congress reenacted the Patent Act.‚Äù</message> 

 <example correction="more evidence|other evidence">On remand, however, the parties will be able to introduce <marker>further evidence</marker> on this point.</example> 

 <example> They had further evidence of the conspiracy.</example> 

# Action to take:
change second token

Specific Actions:
Replace token #2 of the antipattern as well as token #2 of the pattern with the following:

<token>proof</token>

Delete the second example in the message element, specifically

'**Example** from Justice Alito: ‚ÄúPost-1952 judicial decisions addressing assignor estoppel supply yet **more evidence** that the status of the doctrine was (at best) uncertain when Congress reenacted the Patent Act.‚Äù'

Replace the word "evidence" with the word "proof" in the '<example correction="'>' element, specifically in the 'correction="(....)"' attribute and in the nested phrase.

Replace the word "evidence" with the word "proof" in the '<example>They had further evidence of the conspiracy.</example>' element.

# Modified Rule:
"""
from domain.modifier_prompts.common_instructions import (
    INSTRUCTION_INTRO,
    RULE_TAG_CLEANING, 
    RULE_TAG_CREATION,
    SYMBOL_REPLACEMENT,
    ADD_SHORT_TEMPLATE,
    ELEMENT_ORDER_RULES
)

# Add tokens before and after
SYSTEM_PROMPT = f"""{INSTRUCTION_INTRO}

# Section 1:
Modify the xml according to the specific actions by adding tokens before and after.

Example 1:
 Specific action:  ( and day ) for the remainder of ( her his )
Origin pattern:
<pattern> 
   <token>for</token> 
   <token min="0">entire</token> 
   <token>remainder</token> 
   <token>of</token> 
 </pattern> 
The origin pattern has 4 tokens so we add new tokens to # 1 and # 6.

(1) Add a new first token to the pattern:  

( and day )

(2) Add a new final token to the pattern:

( her his )

(3) Please change the existing '<example correction="' element so that it matches the new modified pattern with the added tokens.

(4) Add references to the new tokens #1 and  #6 to the suggestion element so that it reads:

<suggestion>\1 for the rest of \6</suggestion> 

Example 2:
 Specific action:  ( and day her ) for the remainder of ( her his my)
Origin pattern:
<pattern> 
   <token>for</token> 
   <token min="0">entire</token> 
   <token>of</token> 
 </pattern> 
The origin pattern has 3 tokens so we add new tokens to # 1 and # 5.

(1) Add a new first token to the pattern:  

( and day )

(2) Add a new final token to the pattern:

( her his )

(3) Please change the existing '<example correction="' element so that it matches the new modified pattern with the added tokens.

(4) Add references to the new tokens #1 and  #5 to the suggestion element so that it reads:

<suggestion>\1 for the rest of \5</suggestion> 

# Section 2:
(1) For the given words provided under Section 1, create tokens based on the following logic: 
- For Regular Words: If a single word is by itself and not in a (parenthesis), then this is an individual token. 
- If a word is of a set surrounded by parenthesis, then this token is a regular expression token that will need to account for all of the words within the parenthesis, with each separated by a "|" character. Punctuation is its own token. Possessives are chunked as tokens splitting at the punctuation mark. So in Ross's, "Ross" is one token, "'s" is the second token. In Business', "Business" is one token, "'" is the second token. An open token, which is indicated with ‘RX(.*?)’ is coded as <token/>.  

Example Input: There (is was) a fight.  
Expected Output:  
<pattern>  
<token>there</token>  
<token regexp="yes">is|was</token>  
<token>a</token>  
<token>fight</token>  
<token>.</token>  
<pattern>  

(2) {RULE_TAG_CLEANING}

(3) {RULE_TAG_CREATION} 

(4) {SYMBOL_REPLACEMENT}

(5) {ADD_SHORT_TEMPLATE}

(6) {ELEMENT_ORDER_RULES}
"""

USER_EXAMPLE = """
# Original Rule:
BRIEFCATCH_41674887511908524498008803174105362964
BRIEFCATCH_PUNCHINESS_827 

<pattern> 

   <token>for</token> 

   <token>the</token>

   <token min="0">entire</token> 

   <token>remainder</token> 

   <token>of</token> 

 </pattern> 

 <suggestion>for the rest of</suggestion> 

 <message>Would shorter words add punch?|**Example** from Justice Kavanaugh: ‚Äú[T]hey are legally and contractually entitled to receive those same monthly payments **for the rest of** their lives.‚Äù|**Example** from Paul Clement: ‚Äú[S]everability is an inquiry into the remedial consequences **for the rest of** a statute of invalidating a successfully challenged provision.‚Äù|**Example** from Joe Palmore: ‚ÄúWin or lose, Plaintiffs will receive the exact same pension payments **for the rest of** their lives.‚Äù</message> 

<example correction="for the rest of">They recognized POAM <marker>for the remainder of</marker> the CBA.</example> 

# Action to take:
add tokens before and after

Specific Actions:
( and day her him it me them there you ) for the remainder of ( her his my our the their us your )

# Modified Rule:
"""

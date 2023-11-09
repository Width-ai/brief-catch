from domain.modifier_prompts.common_instructions import (
    INSTRUCTION_INTRO,
    RULE_TAG_CLEANING, 
    RULE_TAG_CREATION,
    SYMBOL_REPLACEMENT,
    ADD_SHORT_TEMPLATE,
    ELEMENT_ORDER_RULES
)

# Add token at end requiring one of these words
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
BRIEFCATCH_75803361340040807034346159244094965068 BRIEFCATCH_PUNCHINESS_621 

<antipattern> 

   <token>for</token> 

   <token>the</token> 

   <token case_sensitive="yes">protection</token> 

   <token>of</token> 

   <token regexp="yes">children|health|human|investors|public</token> 

 </antipattern> 

 <antipattern> 

   <token>or</token> 

   <token>for</token> 

   <token>the</token> 

   <token case_sensitive="yes">protection</token> 

   <token>of</token> 

 </antipattern> 

 <antipattern> 

   <token>,</token> 

   <token>for</token> 

   <token>the</token> 

   <token case_sensitive="yes">protection</token> 

   <token>of</token> 

 </antipattern>  

<pattern> 

   <token>for</token> 

   <token>the</token> 

   <token case_sensitive="yes">protection</token> 

   <token>of</token> 

 </pattern> 

 <message>Could you convert this **noun to a verb** here to strengthen the sentence?|**Example** from Justice Breyer: ‚ÄúOne side believes the right essential **to protect** the lives of those attacked in the home; the other side believes it essential to regulate the right in order to protect the lives of others attacked with guns.‚Äù|**Example** from John Quinn: ‚ÄúFinally, if this Court deems a preliminary injunction to be necessary, [Defendant] should post a bond **to protect** Defendant‚Äôs costs and damages if the injunction is improvidently granted.‚Äù|A **nominalization** is a noun created from a verb (such as **utilization** and **expansion**) or from an adjective (such as **applicability** and **safety**). |Changing **nominalizations** back to verbs often makes writing livelier.</message> 

<suggestion>to protect</suggestion> 

 <suggestion>for protecting</suggestion> 

 <example correction="to protect|for protecting">The court exercised its discretion <marker>for the protection of</marker> the jurors' privacy.</example> 

 <example>This was for the protection of children.</example> 

 <example>It was for this or for the protection of children.</example> 

 <example>But, for the protection of the plaintiff, we said no.</example> 

# Action to take:
add token at end requiring one of these words

Specific Actions:
Add the following token to the pattern as well as the as the second, third, and forth antipattern of the below xml rule as their final token, respectively:

<token regexp="yes">the|her|them|and|themselves|his|its|a</token> 

Delete first antipattern in the rule as well as the corresponding example element (" <example>This was for the protection of children.</example> ").

Add the new token #5 to the suggestions so that they read:

<suggestion>to protect \5</suggestion> 

<suggestion>for protecting \5</suggestion>

Modify the second last example phrase (' <example>It was for this or for the protection of the partner.</example> ') so that it matches the new modified antipattern it corresponds to.

# Modified Rule:
"""

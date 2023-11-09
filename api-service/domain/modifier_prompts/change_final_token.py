from domain.modifier_prompts.common_instructions import (
    INSTRUCTION_INTRO,
    ANTIPATTERN_TOKEN_RULES,
    PARTS_OF_SPEECH_TAGS,
    TOKEN_CREATION_EXAMPLES,
    EXAMPLES_FOR_ANTIPATTERNS,
    RULE_TAG_CLEANING, 
    RULE_TAG_CREATION,
    SYMBOL_REPLACEMENT,
    ADD_SHORT_TEMPLATE,
    ELEMENT_ORDER_RULES
)

# Change final token so it requires one of these words
SYSTEM_PROMPT = f"""{INSTRUCTION_INTRO}

# Section 1:  

(1) <antipattern>: Each antipattern begins with this exact line.  

An antipattern is comprised of only tokens, each of which begin with ‘<token>’ and close with ‘</token>’.  

</antipattern> Each antipattern closes with this exact line.  

(2) All antipatterns need to be located below the ‘<rule’ opening tag and above the ‘<pattern>’ opening tag within the xml rule in Input 4. In case the xml rule provided in Input 4 already contains one or more antipattern(s), assign numbers to each of the existing antipatterns, beginning at #1 for the first line that has "<antipattern …" in it. Moving down vertically you should add 1 for each subsequent opening "<antipattern …" tag in the rule, making then next token #2. And so on. Find the location of the requested antipattern input from Input 1, and insert the new antipattern into the code from Input 4 at the given position within the code.  

(3) {ANTIPATTERN_TOKEN_RULES} 

{PARTS_OF_SPEECH_TAGS}

{TOKEN_CREATION_EXAMPLES} 

(4) {EXAMPLES_FOR_ANTIPATTERNS}

# Section 2:
(1) {RULE_TAG_CLEANING}

(2) {RULE_TAG_CREATION}

(3) {SYMBOL_REPLACEMENT}

(4) {ADD_SHORT_TEMPLATE}

(5) {ELEMENT_ORDER_RULES}"""

USER_EXAMPLE = """
# Original Rule:
BRIEFCATCH_5990191730927097327234561913918938571BRIEFCATCH_PUNCHINESS_575 

<antipattern> 

   <token>for</token> 

   <token min="0" regexp="yes">clear|flagrant|blatant</token> 

   <token regexp="yes">violation|violations</token> 

   <token>of</token> 

   <token regexp="yes">any|federal|his|human|international|section|such|this</token>

 </antipattern> 

<pattern> 

   <token>for</token> 

   <token min="0" regexp="yes">clear|flagrant|blatant</token> 

   <token regexp="yes">violation|violations</token> 

   <token>of</token> 

 </pattern> 

<message>Would replacing this **nominalization** with an action strengthen the sentence?|**Example** from Justice Kagan: ‚Äú[T]he civil penalties **for violating** Notice 2016‚Äì66 are tax penalties[.]‚Äù|**Example** from Justice Breyer: ‚ÄúSuppose a noncitizen‚Äôs previous conviction was **for violating** State Statute ¬ß 123.‚Äù|**Example** from Greg Garre: ‚ÄúThe government acknowledges that its employees can act with confidence that their mistakes will not expose them to liability **for violating** federal law[.]‚Äù|A **nominalization** is a noun created from a verb (such as **utilization** and **expansion**) or from an adjective (such as **applicability** and **safety**). |Changing **nominalizations** back to verbs often makes writing livelier.</message> 

<suggestion>for violating</suggestion> 

 <example correction="for violating">The ordinance allowed the prosecutions <marker>for violations of</marker> the local laws.</example> 

 <example>He was arrested for clear violations of federal law.</example>

# Action to take:
change final token so it requires one of these words

Specific Actions:
Replace the final token of the antipattern with:

<token regexp="yes">a|his|these|an|this|local</token>

# Modified Rule:
"""

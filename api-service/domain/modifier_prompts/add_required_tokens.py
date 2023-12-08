from domain.modifier_prompts.common_instructions import (
    INSTRUCTION_INTRO,
    PARTS_OF_SPEECH_TAGS,
    TOKEN_CREATION_EXAMPLES,
    RULE_TAG_CLEANING, 
    RULE_TAG_CREATION,
    SYMBOL_REPLACEMENT,
    ADD_SHORT_TEMPLATE,
    ELEMENT_ORDER_RULES
)


# Add required tokens both before and after the string
SYSTEM_PROMPT = f"""{INSTRUCTION_INTRO}

# Section 1:

Add new tokens to the xml rule in Input 4, as needed, based on the info provided in Input 1 and following the below instructions:  

(1) <token>: Each tokens begins with this exact line.  

A token is comprised of one or more options. These can be words/lettes/numbers/symbols. 

</token> Each tokens closes with this exact line.  

(2) All tokens need to be nested within the ‘<pattern>’ opening tag and the closing ‘</pattern>’ tag within the xml rule in Input 4. In case the xml rule provided in Input 4 already contains one or more tokens within the existing pattern, assign numbers to each of the existing tokens, beginning at #1 for the first line within the pattern that has "<token>" in it. Moving down vertically you should add 1 for each subsequent opening "<token>" tag in the pattern, making then next token #2. And so on. Find the location of the requested token input from Input 1, and insert the new tokens into the code from Input 4 at the given position within the code. Review the tokens in the existing pattern and match them up with the string of words and word options provided under Input 1. Words or word options from the string under Input 1 that are already contained within the pattern in a token at the exact same position of the sequence, should be retained. Words or word options that are not yet - fully - contained in a token within the pattern should be added as a token following the below instruction. A particular set of word options which is already partially contained in a token within the pattern in the same position as in the sequence under Input 1, may be enhanced to encompass the additional options listed for that token and position within the string provided under Input 1.

(3) Once the new tokens have been added, reassign new numbers to each token and modify the referenced tokens in the suggestion element to reflect the made changes and the newly assigned token numbers. Additional tokens should be added within all suggestion elements at their respective position within the string of words in the pattern's new token sequence. Existing references to tokens in the suggestion elements should be modified according to the newly assigned token numbers.

(4) For the <tokens> nested within the pattern please follow the below instructions to properly write the token lines of an pattern.  

Create a string of tokens matching the string of text provided in Input 1.  

For the string of words provided under Input 1 below ‘Add antipattern #:’ create tokens based on the following logic:   

- For Regular Words: If a single word is by itself and not in a (parenthesis), then this is an individual token. If a word is of a set surrounded by parenthesis, then this token is a regular expression token that will need to account for all of the words within the parenthesis, with each separated by a "|" character. Punctuation is its own token. Possessives are chunked as tokens splitting at the punctuation mark. So in Ross's, "Ross" is one token, "'s" is the second token. In Business', "Business" is one token, "'" is the second token. An open token, which is indicated with ‘RX(.*?)’ is coded as <token/>. 
Example Input: There (is was) a fight.  
Expected Output:  
<antipattern>  
<token>there</token>  
<token regexp="yes">is|was</token>  
<token>a</token>  
<token>fight</token>  
<token>.</token>  
<antipattern>  

{PARTS_OF_SPEECH_TAGS}  

{TOKEN_CREATION_EXAMPLES}

(5) For each token that is added or modified, the example phrase in the example correction element needs to be modified in such way that it matches the new modified string of tokens and words within the pattern. The exemple phrase absolutely needs to match the exact string of tokens of the pattern. The phrase also needs to constitute a full coherent sentence, it should be short but make up a complete and logical phrase.

#####################  

# Section 2:
(1) {RULE_TAG_CLEANING} 

(2) {RULE_TAG_CREATION}

(3) {SYMBOL_REPLACEMENT}

(4) {ADD_SHORT_TEMPLATE}

(5) {ELEMENT_ORDER_RULES}
"""


USER_EXAMPLE = """
# Original Rule:
BRIEFCATCH_234447315474581040737958218292873413798BRIEFCATCH_FRESH_LANGUAGE_3336 

<pattern> 

   <token>an</token> 

   <token>individual</token> 

   <token>who</token> 

 </pattern> 

 <suggestion>a person who</suggestion> 

 <suggestion>someone who</suggestion> 

 <suggestion>anyone who</suggestion> 

 <message>Could **individual** come across as pretentious, legalistic, or vague?|**Example** from Chief Justice Roberts: ‚ÄúThe warrantless search of a home . . . remains lawful when officers obtain the consent of **someone who** reasonably appears to be but is not in fact a resident.‚Äù|**Example** from Justice Ketanji Jackson: ‚ÄúBefore DHS decides to authorize the swift ejection of **someone who** lives in the interior of the country . . . .‚Äù</message> 

 <example correction="a person who|someone who|anyone who">SORA requires <marker>an individual who</marker> is convicted of.</example> 

# Action to take:
Add required tokens both before and after the string

Specific Actions:
( of to is that as by for with means requires ) an individual who ( is has was had does would could )

# Modified Rule:
"""

INSTRUCTION_INTRO = """You will be given a rule, an element type to modify, and an action to take with specificities around the action in the user text. Modify the xml rule according to the info provided in sections 1 and 2."""


ANTIPATTERN_RULES = """Antipatterns begin and end with their tags on separate lines and only contains tokens that also have their respective tags:
<antipattern>
<token>...</token>
...
</antipattern>
"""

ANTIPATTERN_POSITIONING = """All antipatterns need to be located below the ‘<rule’ opening tag and above the ‘<pattern>’ opening tag within the xml rule in Input 4. In case the xml rule provided in Input 4 already contains one or more antipattern(s), assign numbers to each of the existing antipatterns, beginning at #1 for the first line that has "<antipattern …" in it. Moving down vertically you should add 1 for each subsequent opening "<antipattern …" tag in the rule, making then next token #2. And so on. Find the location of the requested antipattern input from Input 1, and insert the new antipattern into the code from Input 4 at the given position within the code."""


ANTIPATTERN_TOKEN_RULES = """For the <tokens> nested within the antipattern please follow the below instructions to properly write the token lines of an antipattern.  

Create a string of tokens based on the following logic:   
- For Regular Words: If a single word is by itself and not in a (parenthesis), then this is an individual token. If a word is of a set surrounded by parenthesis, then this token is a regular expression token that will need to account for all of the words within the parenthesis, with each separated by a "|" character.

- Punctuation is its own token.

- Possessives are chunked as tokens splitting at the punctuation mark. So in Ross's, "Ross" is one token, "'s" is the second token. In Business', "Business" is one token, "'" is the second token. An open token, which is indicated with ‘RX(.*?)’ is coded as <token/>.  

For example, with the input: There (is was) a fight.  
The output would be: 

<antipattern>  
<token>there</token>  
<token regexp="yes">is|was</token>  
<token>a</token>  
<token>fight</token>  
<token>.</token>  
<antipattern>
"""


PARTS_OF_SPEECH_TAGS = """- Part-of-Speech Tags: These tokens take one of two forms: <token postag="POSTAG"/> or <token postag_regexp="yes" postag="CC|CD"/>. The postag_regexp="yes" line is required when either (i) there are more than one postag sought to be matched by the token; or (ii) when you use a broad part-of-speech tag that can capture several types of postags. An example would be V.*. This means any POSTAG that begins with V. So this would match a word that is tagged as VB, VBD, VBG, VBN, VBP, and VBZ. If you used N.*, this would match any word tagged as NN, NNS, NN:U, NN:UN, NNP, and NNPS. Here is the total list of part-of-speech tags currently recognized that you can use (the capital letters at the beginning are the actual tags you should use instead of "POSTAG" in the example above):  
CC Coordinating conjunction: and, or, either, if, as, since, once, neither  

CD Cardinal number: one, two, twenty-four  

DT Determiner: a, an, all, many, much, any, some, this  

EX Existential there: there (no other words)  

FW Foreign word: infinitum, ipso  

IN Preposition/subordinate conjunction: except, inside, across, on, through, beyond, with, without  

JJ Adjective: beautiful, large, inspectable  

JJR Adjective, comparative: larger, quicker  

JJS Adjective, superlative: largest, quickest  

LS List item marker: not used by LanguageTool  

MD Modal: should, can, need, must, will, would  

NN Noun, singular count noun: bicycle, earthquake, zipper  

NNS Noun, plural: bicycles, earthquakes, zippers  

NN:U Nouns that are always uncountable #new tag - deviation from Penn, examples: admiration, Afrikaans  

NN:UN Nouns that might be used in the plural form and with an indefinite article, depending on their meaning #new tag - deviation from Penn, examples: establishment, wax, afternoon  

NNP Proper noun, singular: Denver, DORAN, Alexandra  

NNPS Proper noun, plural: Buddhists, Englishmen  

ORD Ordinal number: first, second, twenty-third, hundredth #New tag (experimental) since LT 4.9. Specified in disambiguation.xml. Examples: first, second, third, twenty-fourth, seventy-sixth  

PCT Punctuation mark: (`.,;:…!?`) #new tag - deviation from Penn  

PDT Predeterminer: all, sure, such, this, many, half, both, quite  

POS Possessive ending: s (as in: Peter's)  

PRP Personal pronoun: everyone, I, he, it, myself  

PRP$ Possessive pronoun: its, our, their, mine, my, her, his, your  

RB Adverb and negation: easily, sunnily, suddenly, specifically, not  

RBR Adverb, comparative: better, faster, quicker  

RBS Adverb, superlative: best, fastest, quickest  

RB_SENT Adverbial phrase including a comma that starts a sentence. #New tag (experimental) since LT 4.8. Specified in disambiguation.xml. Examples: However, Whenever possible, First of all, On the other hand,  

RP Particle: in, into, at, off, over, by, for, under  

SENT_END: LanguageTool tags the last token of a sentence as both SENT_END and a regular part-of-speech tag.  

SENT_START: LanguageTool tags the first token of a sentence as both SENT_START and a regular part-of-speech tag.   

SYM Symbol: rarely used by LanguageTool (e.g. for 'DD/MM/YYYY')  

TO to: to (no other words)  

UH Interjection: aargh, ahem, attention, congrats, help  

VB Verb, base form: eat, jump, believe, be, have  

VBD Verb, past tense: ate, jumped, believed  

VBG Verb, gerund/present participle: eating, jumping, believing  

VBN Verb, past participle: eaten, jumped, believed  

VBP Verb, non-3rd ps. sing. present: eat, jump, believe, am (as in 'I am'), are  

VBZ Verb, 3rd ps. sing. present: eats, jumps, believes, is, has  

WDT wh-determiner: that, whatever, what, whichever, which (no other words)  

WP wh-pronoun: that, whatever, what, whatsoever, whomsoever, whosoever, who, whom, whoever, whomever, which (no other words)  

WP$ Possessive wh-pronoun: whose (no other words)  

WRB wh-adverb: however, how, wherever, where, when, why  

`` Left open double quote  

, Comma  

'' Right close double quote  

. Sentence-final punctuation (in LanguageTool, use SENT_END instead)  

: Colon, semi-colon  

$ Dollar sign  

# Pound sign"""


TOKEN_CREATION_EXAMPLES = """Here are some examples for creating tokens:

Example Input: I like to VB  
Expected Output: 

<antipattern>  
<token>I</token>  
<token>like</token>  
<token>to</token>  
<token postag=”VB”/>  
<antipattern>  


Example Input: I like ( NNP NNS )  
Expected Output:  

<antipattern>  
<token>I</token>  
<token>like</token>  
<postag_regexp="yes" postag="NNP|NNS"/>  
<antipattern>  


Example Input: I like N.*  
Expected Output:  

<antipattern>  
<token>I</token>  
<token>like</token>  
<token postag_regexp="yes" postag="N.*">  
<antipattern>  

- Exceptions: Exceptions come between the <token> and </token> lines of code. They except words that would be matched otherwise by the part-of-speech tag used by the token. If there is a single exception, then it can be added like this: <exception>exception</exception> (excepts the word exception). If there are several, then like a token you must add the regexp="yes attribute and separate the exception words with the "|" character: <exception regexp="yes">single|exception</exception> (excepts the words single and exception from the token).  

Input 1 will indicate exceptions by preceding the words to be excepted by a "!" character.  

Example Input: (VB !swim !run !walk) 
(Comment: Here the token should match "VB" but the words "swim" "run" and "walk" should be excepted.) 
Example Output:   
<antipattern>  
<token postag="VB">  
<exception regexp="yes">swim|run|walk</exception>  
</token>  
</antipattern>  

Note: For both tokens and exceptions that include several words, always order the words in alphabetical order.   

Complex exceptions: POSTAGS & words. Sometimes the exceptions will need to include both postags and enumerated words. In this case, the two must be in separate exception lines (you can't mix and match).   

Example Input: V.* (!VBD !swim !run !walk)
(Comment: Here the token should match "VB" but the words "swim" "run" and "walk" should be excepted)  
Expected Output:   
<antipattern>  
<token postag_regexp="yes" postag="V.*">  
<exception postag="VBD"/>  
<exception regexp="yes">swim|run</exception>  
</token>  
</antipattern>  

- Inflection: An inflected token with one or more words will be indicated by preceding it with "CT" and surrounding the word or words in parenthesis: CT(walk run !ran). This means you would create a token with the property "inflected="yes"" for the words walk|run, and then you would add a single exception for the word "ran":  

<token inflected="yes">walk|run  
<exception>ran</exception>
</token>  

- Case Sensitive: Another token property is case_sensitive="yes" which can be used to specify that the match word must be upper or lower case. By default case_sensitive="no". If the token needs to be case_sensitive="yes," this will be requestes by putting a "/" character before the word whose token should have the case_sensitive="yes" attribute: "/They"  <token case_sensitive="yes">They</token>  

- Sent_Start Coding: Sent_Start is a POSTAG that counts as its own token at the start of the sentence. This means if Input 1 requests "SENT_START Hello" Then token 1 is <token postag="SENT_START"/>, token 2 is <token>hello</token>. When Sent_Start is used, the rest of the pattern must be offset from this token using <marker> </marker>.

Example Input: SENT_START due to the fact tha  
Expected Output:  
<antipattern>  
<token postag="SENT_START"/>  
<token>due</token>
<token>to</token>
<token>the</token>
<token>fact</token>
<token>that</token>
</antipattern>
"""


EXAMPLES_FOR_ANTIPATTERNS = """For each antipattern that is added, an example needs to be added with an exemplary phrase that absolutely needs to match the exact string of tokens of the antipattern(s). So at the bottom of the rule, right above the rule-closing line ( </rule>) you will insert a line that tests the antipattern like this: <example>This test sentence should trigger the antipattern.</example>. Please generate an exemplary phrase yourself which matches the newly added antipattern and insert it into the rule following the before instructions (add the following element and insert the self-generated phrase into the {placeholder} field:  

<example>{placeholder}</example>  

In case the rule already contains antipatterns and examples for those antipatterns, add a new example for the newly added antipattern and insert it below after all other existing examples above the closing </rule> tag."""


RULE_TAG_CLEANING = """Delete all ‘,’ symbols following the ‘BRIEFCATCH_{number}’, the ‘BRIEFCATCH_{CATEGORYNAME}_{number}’, the ‘</pattern>’, each ‘</suggestion>, ‘</message>’, and ‘</example>’ object in the code provided in the input. Do not delete any other ‘,’ symbols in the code other than the ones specifically listed in the before sentence. Delete all spaces preceding or succeeding any "<" and ">" symbols in the code."""


RULE_TAG_CREATION = """Insert a rule opening tag at the top of the new rule following this example:
Example Input: BRIEFCATCH_311798533127983971246215325355996953264, BRIEFCATCH_PUNCHINESS_847.2,  
Expected Output: <rule id="BRIEFCATCH_311798533127983971246215325355996953264" name="BRIEFCATCH_ PUNCHINESS_847.2 >"""


SYMBOL_REPLACEMENT = """In the <message>(….)</message> element of the code in the input, replace all “‚Äù” symbols with quotation marks, and all “‚Äî” symbols with a m-dash symbol. Leave all the '[' and ']' as is in the message element."""


ADD_SHORT_TEMPLATE = """Add the below template to the modified rule, right below the last of the ‘</suggestion>’ tags in the code and above the first ‘<example’ tag in the code. Also replace the part reading ‘BRIEFCATCH_PUNCHINESS_847.2’ in the template with the second line of the input (without the ‘,’ symbol succeeding it). Also count the number of existing </suggestion> tags in the code in the input and replace the number ‘1’ behind ‘"correctionCount":’ in the below template with the number of suggestions you have counted in the code in the input following the given instructions.
Template:  
<short>{"ruleGroup":"BRIEFCATCH_PUNCHINESS_847.2","ruleGroupIdx":1,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"5.223"}</short>   """


ELEMENT_ORDER_RULES = """The elements in the modified rule need to be in the following order: 

1. ‘<rule(…)’ {rule opening tag} 
2. <antipattern>(tokens)</antipattern> {all antipatterns one after another} 
3. <pattern>tokens</pattern> {pattern} 
4. <message>(…..)</message> {message} 
5. <suggestion>(…..)</suggestion> {all suggestions one after another} 
6. <short>(…..)</short> {short} 
7. <example correction=”(….)”>(…..)</example> {example for the pattern} 
8. <example>(….)</example> {all examples for antipatterns one after another} 
9. “</rule>” {closing rule tag}"""


PATTERN_CLARIFICATION = """pattern is not antipattern"""



STANDARD_PROMPT = f"""{INSTRUCTION_INTRO}
# Section 1:

(1) {ANTIPATTERN_RULES}

(2) {ANTIPATTERN_POSITIONING}

(3) {ANTIPATTERN_TOKEN_RULES}

{PARTS_OF_SPEECH_TAGS}

{TOKEN_CREATION_EXAMPLES}

(4) {EXAMPLES_FOR_ANTIPATTERNS}


# Section 2:
(1) {RULE_TAG_CLEANING}

(2) {RULE_TAG_CREATION}

(3) {SYMBOL_REPLACEMENT}

(4) {ADD_SHORT_TEMPLATE}

(5) {ELEMENT_ORDER_RULES}
"""
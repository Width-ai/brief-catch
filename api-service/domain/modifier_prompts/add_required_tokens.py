# Add required tokens both before and after the string
SYSTEM_PROMPT = """
You will be given an original rule as "Input 4", an action to take and specificities around the action as "Input 1" in the user text. Modify the original rule according to the info provided in sections 1 and 2.

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

Example:   

Example Input: There (is was) a fight.  

Example Output:  

<antipattern>  

<token>there</token>  

<token regexp="yes">is|was</token>  

<token>a</token>  

<token>fight</token>  

<token>.</token>  

<antipattern>  

- Part-of-Speech Tags: These tokens take one of two forms: <token postag="POSTAG"/> or <token postag_regexp="yes" postag="CC|CD"/>. The postag_regexp="yes" line is required when either (i) there are more than one postag sought to be matched by the token; or (ii) when you use a broad part-of-speech tag that can capture several types of postags. An example would be V.*. This means any POSTAG that begins with V. So this would match a word that is tagged as VB, VBD, VBG, VBN, VBP, and VBZ. If you used N.*, this would match any word tagged as NN, NNS, NN:U, NN:UN, NNP, and NNPS. Here is the total list of part-of-speech tags currently recognized that you can use (the capital letters at the beginning are the actual tags you should use instead of "POSTAG" in the example above):  

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

# Pound sign  

Example 1:   

Example Input: I like to VB  

Example Output:  

<antipattern>  

<token>I</token>  

<token>like</token>  

<token>to</token>  

<token postag=”VB”/>  

<antipattern>  

Example 2:   

Example Input: I like ( NNP NNS )  

Example Output:  

<antipattern>  

<token>I</token>  

<token>like</token>  

<postag_regexp="yes" postag="NNP|NNS"/>  

<antipattern>  

Example 3:  

Example Input: I like N.*  

Example Output:  

<antipattern>  

<token>I</token>  

<token>like</token>  

<token postag_regexp="yes" postag="N.*">  

<antipattern>  

- Exceptions: Exceptions come between the <token> and </token> lines of code. They except words that would be matched otherwise by the part-of-speech tag used by the token. If there is a single exception, then it can be added like this: <exception>exception</exception> (excepts the word exception). If there are several, then like a token you must add the regexp="yes attribute and separate the exception words with the "|" character: <exception regexp="yes">single|exception</exception> (excepts the words single and exception from the token).  

Input 1 will indicate exceptions by preceding the words to be excepted by a "!" character.  

Example 1:   

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

Example 1:   

Example Input: V.* (!VBD !swim !run !walk)  

(Comment: Here the token should match "VB" but the words "swim" "run" and "walk" should be excepted)  

Example Output:   

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

Example 1:   

Example Input: SENT_START due to the fact that

Example Output:  

<antipattern>  
<token postag="SENT_START"/>
<marker> 
<token>due</token>  
<token>to</token>  
<token>the</token>  
<token>fact</token>  
<token>that</token> 
</marker> 
</antipattern>  

(5) For each token that is added or modified, the example phrase in the example correction element needs to be modified in such way that it matches the new modified string of tokens and words within the pattern. The exemple phrase absolutely needs to match the exact string of tokens of the pattern. The phrase also needs to constitute a full coherent sentence, it should be short but make up a complete and logical phrase.

#####################  

# Section 2:

(1) Delete all ‘,’ symbols following the ‘BRIEFCATCH_{number}’, the ‘BRIEFCATCH_{CATEGORYNAME}_{number}’, the ‘</pattern>’, each ‘</suggestion>, ‘</message>’, and ‘</example>’ object in the code provided in Input 4. Do not delete any other ‘,’ symbols in the code other than the ones specifically listed in the before sentence. Delete all spaces preceding or succeeding any "<" and ">" symbols in the code. 

(2) Insert the following rule opening tag template at the top of the new rule, replacing the first set of ‘#” symbols contained therein with the number following ‘BRIEFCATCH_ ‘ in the first line of the code in Input 4, and the second set of ‘#” symbols with the number following ‘BRIEFCATCH_{CATEGORYNAME}_’ in the second line of the code in Input 4. Also replace the placeholder ‘CATEGORYNAME’ in the below rule opening tag template with the given CATEGORYNAME in the the second line of the code in Input 4 after “BRIEFCATCH_” and before “_”.  

Template for rule opening tag:  

<rule id="BRIEFCATCH_########################################" name="BRIEFCATCH_CATEGORYNAME_#####>  

Example:   

Example Input: BRIEFCATCH_311798533127983971246215325355996953264, BRIEFCATCH_PUNCHINESS_847.2,  

Example Output: <rule id="BRIEFCATCH_311798533127983971246215325355996953264" name="BRIEFCATCH_ PUNCHINESS_847.2 >  

(3) Once you have completed the instruction in (2), delete the first two lines of the code in Input 4 (so both the ‘BRIEFCATCH_{number}’ and the ‘BRIEFCATCH_{CATEGORYNAME}_{number}’ objects).  

(4) In the <message>(….)</message> element of the code in Input 4, replace all “‚Äù” symbols with quotation marks, and all “‚Äî” symbols with a m-dash symbol.  Leave all the '[' and ']' as is in the message element.

(5) Add the below template to the code in Input 4, right below the last of the ‘</suggestion>’ tags in the code and above the first ‘<example’ tag in the code. Also replace the part reading ‘RIEFCATCH_PUNCHINESS_847.2’ in the template with the second line of Input 4 (without the ‘,’ symbol succeeding it). Also count the number of existing </suggestion> tags in the code in Input 4 and replace the number ‘1’ behind ‘"correctionCount":’ in the below template with the number of suggestions you have counted in the code in Input 4 following the given instructions.  

Template:  

<short>{"ruleGroup":"BRIEFCATCH_PUNCHINESS_847.2","ruleGroupIdx":1,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"5.223"}</short>   

(6) Add a ‘</rule>’ closing tag at the very end of the code in Input 4 right below the last closing ‘</example>’ tags contained in the code.  

(7) The elements in the modified rule need to be in the following order: 

1. ‘<rule(…)’ {rule opening tag} 

2. <antipattern>(tokens)</antipattern> {all antipatterns one after another} 

3. <pattern>tokens</pattern> {pattern} 

4. <message>(…..)</message> {message} 

5. <suggestion>(…..)</suggestion> {all suggestions one after another} 

6. <short>(…..)</short> {short} 

7. <example correction=”(….)”>(…..)</example> {example for the pattern} 

8. <example>(….)</example> {all examples for antipatterns one after another} 

9. “</rule>” {closing rule tag} 

If any of the elements in the existing rule as provided in Input 4 do not match the above order, rearrange them accordingly to reflect the given order.

(8) Ensure that each '>' symbol at the end of a closing tag is immediately succeeded by the next subsequent '<' symbol of the following opening tag or the next following word/letter/number/single, without any space in between them. Write all of the antipatterns and example elements as well as their respective nested objects each within a single line. Within the <example correction=(.....)>' element, make sure that any opening '<marker>' tag has a single space right before it and that any closing '</marker>' tag is succeeded by a single space. Within the suggestion tag there should be a space between any referenced token number such as for example '\1' and the next subsequent word/letter/number/symbol (e.g. '<suggestion>\1 many</suggestion>').
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

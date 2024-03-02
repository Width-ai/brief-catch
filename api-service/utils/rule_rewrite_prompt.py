import re
from typing import Dict, List
from utils.dynamic_prompting import get_pos_tag_dicts_from_rule
from domain.dynamic_prompting.parts_of_speech import POS_MAPS

RX_PROMPT = """
## Open Token: `RX(.*?)`

- Open tokens are indicated by 'RX(.*?)' 
- Open tokens are coded as <token/>. 
- If you are told to generate a token for a pattern like `( RX(.*? ) !apples !bananas !grapes )`, that would translate to: <token><exception regexp="yes">apples|banans|grapes</exception></token>

Below are a few examples: 
Input: "There (is was) a fight."  
Output:
```
<antipattern>  
    <token>there</token>  
    <token regexp="yes">is|was</token>  
    <token>a</token>  
    <token>fight</token>  
    <token>.</token>  
</antipattern>
```
"""
CT_PROMPT = """
## Infelction: `CT()`

`CT` indicates a token should be inflected. To inflect a token, include the attribute `inflected="yes"` in the token tag. For example, the instructions `CT(call) upon ( a all his me the )` corresponds to the following tokens:
```
<token inflected="yes">call</token>
<token>upon</token>
<token regexp="yes">a|all|his|me|the</token>
```

If asked to include multiple inflected words in a single token, you can use pipe character `|` as a logical OR operator. For example, the instructions `( CT(initiate) CT(make) ) ( contact contacts ) with ( other others people )` contains multiple inflected words (each indicated by CT) in the same token (outer parenthesis marker) and would therefore correspond to the following tokens: 
```
<token inflected="yes">initiate|make</token>  
<token>contact|contacts</token>  
<token>with</token>  
<token>other|others|people</token>  
```

Inflected tokens can contain a combination of regexp and exception. For example, the instructions `CT(walk run !ran)` corresponds to the following token: 
```
<token inflected="yes">walk|run<exception>ran</exception></token>  
```
"""
CASESENS_PROMPT = """
## case sensitive

Case Sensitive: Another token property is case_sensitive="yes". By default case_sensitive="no", if the token needs to be case_sensitive="yes," this will be requested by putting a "/" character before the word whose token should have the case_sensitive="yes" attribute. For example: 
Input:
"/They"
Output:
```
<token case_sensitive="yes">They</token>  
```
"""


def format_optimized_standard_prompt(
    replace_rx,
    replace_ct,
    replace_casesens,
):
    return f"""
    You are a component in a system designed to modify xml content. The user will provide to you an xml content, an element of that xml that should be modified, and a specific modification request. Your job will be to modify the xml content according to the information provided.

    These instructions are formatted as a markdown document into two parts. The first part introduces you to the syntax of the XML content you will be modifying. The second part provides instructions on how to interpret the user input. 

    # PART I: XML Rules
    
    ## Introduction

    The xml content you will be modifying encodes the rules for a software designed to make text edits. The following are the most important tags:

    - `<rule>`: this is the parent tag for a rule
    - `<pattern>`: this encloses a series of token tags, and encodes the snippets of text that the software is looking out for in order to get replaced. Patterns are made of tokens and exceptions.
    - `<antipattern>`: this also encloses a series of token tags, and also encodes the snippets of text that the software is looking out. However, unlike <patterns> which get replaced, antipatterns are not replaced. 
    - `<token>`: a token inside a `<pattern>` tag encodes a token of text. This can either be an entire word, a part-of-speech (POS), or a regular expression (more on these below).
    - `<excetion>`: you will sometimes see exception tags inside token tags. These represent exceptions to the token that should not be matched by that pattern.
    - `<example>`: every pattern and antipattern have a corresponding example tag that exemplifies a snippet of text where that would trigger that pattern or antipattern. More on example tags below. 
    - `<suggestion>`: every pattern and antipattern has one and only one corresponding suggestion tag. Suggestion tags represent the text that the software will suggest as a replacement for the pattern encoded by that rule. 

    
    Here is an example of a simple xml rule:

    ```
    <rule id="BRIEFCATCH_23265665707036495693898601905022857498" name="BRIEFCATCH_PUNCHINESS_778">
        <pattern>
            <token>further</token>
            <token>proof</token>
        </pattern>
        <suggestion>more <match no="2"/></suggestion>
        <example correction="more proof">The parties will be able to introduce <marker>further proof</marker> on this point.</example>
    </rule>
    ```
    
    Below we will discuss the rules for making valid tags.

    ## Pattern <pattern> tags

    Patterns represent text that is supposed to be replaced. Patterns also begin and end with their tags on separate lines.

    ### Pattern <example> tags

    - An example tag associated with a pattern has a correction attribute. This correction attribute indicates what the text that matches the pattern should be corrected to.
    - An example tag associated with a pattern has <marker>...</marker> tags to surround the specific text enclosed by the example tag matches its corresponding pattern.

    
    ## Antipattern <antipattern> tags 
    
    Antipatterns represent text that is not supposed to be replaced. Antipatterns begin and end with their tags on separate lines.

    ### Antipattern <example> tags

    - An example tag that goes with an antipattern does not have any attributes. They provide an example of text that is captured by the tokens of the antipattern.
    

    ## Token <token> tags 

    Patterns and antipatterns are defined by tokens. Tokens are encoded by <token> tags. These define the specific elements within patterns and antipatterns that the software should identify. They can match specific words, parts of speech, or regular expressions. 

    Importantly, tokens can contain `<exception>` tags. These define specific words or patterns that should not be matched by the token, even if they fit the other criteria specified.

    - Punctuation is its own token.
    - Possessives are chunked as tokens splitting at the punctuation mark. So in Ross's, "Ross" is one token, "'s" is the second token. In Business', "Business" is one token, "'" is the second token.

    ### Logical OR operator

    Tokens may contain a logical OR operator, signified by "|". This allows the tag to match multiple words. For example, the following tokens:
    ```
    <token>assisted</token>
    <token regexp="yes">in|with</token>
    ```
    match either "assisted in" or "assisted with" substrings.

    ## Part-of-Speech (POS) tags

    Apart from exact words, tokens can also be matched to parts-of-speech (POS). In the XML rules, a POS is expressed using the following abbreviations: 

    - CC: Coordinating conjunction: for, and, nor, but, or, yet, so",
    - CD: Cardinal number: one, two, twenty-four",
    - DT: Determiner: a, an, all, many, much, any, some, this",
    - EX: Existential there: there (no other words)",
    - FW: Foreign word: infinitum, ipso",
    - IN: Preposition/subordinate conjunction: except, inside, across, on, through, beyond, with, without",
    - JJ: Adjective: beautiful, large, inspectable",
    - JJR: Adjective, comparative: larger, quicker",
    - JJS: Adjective, superlative: largest, quickest",
    - JJ:.*: Matches any adjective in the list of JJ, JJR, and JJS. Can be an adjective, comparative adjective, or superlative adjective",
    - LS: List item marker: not used by LanguageTool",
    - MD: Modal: should, can, need, must, will, would",
    - NN: Noun, singular count noun: bicycle, earthquake, zipper",
    - NNS: Noun, plural: bicycles, earthquakes, zippers",
    - NN::U Nouns that are always uncountable #new tag - deviation from Penn, examples: admiration, Afrikaans",
    - NN::UN Nouns that might be used in the plural form and with an indefinite article, depending on their meaning #new tag - deviation from Penn, examples: establishment, wax, afternoon",
    - NNP: Proper noun, singular: Denver, DORAN, Alexandra",
    - NNPS: Proper noun, plural: Buddhists, Englishmen",
    - ORD: Ordinal number: first, second, twenty-third, hundredth #New tag (experimental) since LT 4.9. Specified in disambiguation.xml. Examples: first, second, third, twenty-fourth, seventy-sixth",
    - PCT: Punctuation mark: (`.,;:…!?`) #new tag - deviation from Penn",
    - PDT: Predeterminer: all, sure, such, this, many, half, both, quite",
    - POS: Possessive ending: s (as in: Peter's)",
    - PRP: Personal pronoun: everyone, I, he, it, myself",
    - PRP:$ Possessive pronoun: its, our, their, mine, my, her, his, your",
    - RB: Adverb and negation: easily, sunnily, suddenly, specifically, not",
    - RBR: Adverb, comparative: better, faster, quicker",
    - RBS: Adverb, superlative: best, fastest, quickest",
    - RB_SENT: Adverbial phrase including a comma that starts a sentence. #New tag (experimental) since LT 4.8. Specified in disambiguation.xml. Examples: However, Whenever possible, First of all, On the other hand,",
    - RP: Particle: in, into, at, off, over, by, for, under",
    - SENT_END:: LanguageTool tags the last token of a sentence as both SENT_END and a regular part-of-speech tag.",
    - SENT_START:: LanguageTool tags the first token of a sentence as both SENT_START and a regular part-of-speech tag.",
    - SYM: Symbol: rarely used by LanguageTool (e.g. for 'DD/MM/YYYY')",
    - TO: to: to (no other words)",
    - UH: Interjection: aargh, ahem, attention, congrats, help",
    - VB: Verb, base form: eat, jump, believe, be, have",
    - VBD: Verb, past tense: ate, jumped, believed",
    - VBG: Verb, gerund/present participle: eating, jumping, believing",
    - VBN: Verb, past participle: eaten, jumped, believed",
    - VBP: Verb, non-3rd ps. sing. present: eat, jump, believe, am (as in 'I am'), are",
    - VBZ: Verb, 3rd ps. sing. present: eats, jumps, believes, is, has",
    - WDT: wh-determiner: that, whatever, what, whichever, which (no other words)",
    - WP: wh-pronoun: that, whatever, what, whatsoever, whomsoever, whosoever, who, whom, whoever, whomever, which (no other words)",
    - WP:$ Possessive wh-pronoun: whose (no other words)",
    - WRB: wh-adverb: however, how, wherever, where, when, why"

    To represent a POS, tokens can include a `postag` attribute with one of the POS tags in the list above like so:  `<token postag="`POSTAG`"/>` where `POSTAG` is replaced by one of the allowed POS abbreviations above. For example, the last token in the pattern below matches any Verb, gerund/present participle like eating, jumping, believing, understanding:
    ```
    <pattern>
        <token>assists</token>
        <token regexp="yes">in|with</token>
        <token postag="VBG">
        </token>
    </pattern>
    <example correction="helps understand">it <marker>assists in understanding</marker> the preference</example>
    ```
    
    The postag_regexp="yes" attribute in the token is required whenever either (i) there are more than one postag sought to be matched by the token (with a logical OR operator "|"); or (ii) when you use a broad part-of-speech tag that can capture several types of postags. 
    - Example: `<token postag=V.* postag_regexp="yes"/>`: This means any POSTAG that begins with V. So this would match a word that is tagged as VB, VBD, VBG, VBN, VBP, and VBZ. 
    - Example: `<token postag=N.* postag_regexp="yes"/>`: This would match any word tagged as NN, NNS, NN:U, NN:UN, NNP, and NNPS. 
    - Example: `<token postag="CD|DT" postag_regexp="yes"/>` would match any word tagged as either CD or DT.

    ## OR tokens
    
    The or token allows you to have one of the operands be a POS and the other a word. for example:
    ```
    <pattern>
        <or>
            <token postag="PRP$"/>
            <token>a</token>
        </or>
        <token regexp="yes">motion|motions</token>
        <token>seeking</token>
        <token>to</token>
    </pattern>
    <example correction="moved to">The prosecution <marker>filed a motion seeking to</marker> have the victim.</example>
    ```
    ```
    <pattern>
        <or>
            <token postag="JJR"/>
            <token regexp="yes">a|another|one|1|sole|the|single</token>
        </or>
        <token regexp="yes">way|means</token>
        <token>of</token>
        <token postag="VBG"/>
    </pattern>
    <example correction="one way to vote">And one<marker>way of voting</marker> or applying to vote exists.</example>
    ```
    
    ## Exception <exception> tags 

    Exceptions allow for nuanced control over pattern matching, ensuring that certain words or phrases are excluded from the match criteria defined by their parent token.

    - If there is a single word to be added as an exception, then it can be added like this: <exception>dog</exception> (excepts the word dog).
    - If there are several, then like a token you MUST include the regexp="yes" attribute and separate the words with the "|" character: <exception regexp="yes">cat|dog</exception> (excepts the words cat and dog from the token).

    
    ## Suggestion <suggestion> tags

    Suggestion tags provide the text that will replace the matched pattern.     The `<suggestion>` tags often utilize dynamic elements to construct their recommendations based on the specific content matched by the `<pattern>`. 

    Critically important: You will rarely have to modify suggestion tags. ONLY MODIFY SUGGESTION TAGS WHEN EXPLICITLY REQUESTED TO DO SO.

    ### Dynamic <match> tags in suggestions 

    - Suggestion tags may include `<match>` tags, which dynamically insert text from the matched pattern into the suggestion. The `<match>` tag's `no` attribute corresponds to the order of `<token>` tags within the `<pattern>`, specifying which token's content should be used in the suggestion.


    ## Example <example> tags

    Example tags demonstrate the practical application of rules, showing a before-and-after view of the text. 

    `<example>` tags work in tandem with `<suggestion>` tags to provide recommendations for improving text. Example tags shows how to apply suggestions to the matched pattern and through the `correction` attribute of the `example` tag shows the effect of each suggestion on the matched pattern. 

    Critically improtant: Every pattern and antipattern in the rule has ONE AND ONLY ONE corresponding example tag! 
        - Whenever you add a pattern or antipattern, you must add a corresponding example tag.
            - Only add a new example tag when asked to generate a new pattern or antipatterns. 
        - When modifying a pattern or antipatterns consider whether their corresponding example also needs to be modified.
            - You only need to modify a single example tag whenever you modify a pattern or antipattern.
        

    ### Example tags associated with patterns

    The correction attribute illustrates the application of the suggestion tags to the original text. That is, correction attribute within an <example> tag associated with a <pattern> directly reflects the proposed changes specified in the <suggestion> tags. 

    - The correction attribute may contain multiple corrections separated by a logical OR operator ("|"), indicating alternative corrections that could apply for each suggestion.

    Example tags associated with patterns can also have <marker></marker> tags indicating what portion of the text was matched by the pattern.

    NOTE: If you modify a pattern, do not modify any examples corresponding to antipatterns (i.e. example tags do not contain a correction attribute)

    Below, notice how the text inside the example tags "good faith" matches the <pattern> tags and gets corrected to the <suggestion> tag in the example tag correction attribute:
    ```
    <pattern>
        <token>good</token>
        <token>faith</token>
    </pattern>
    <suggestion>good-faith</suggestion>
    <example correction="good-faith">good faith</example>
    ```
        
    ### Handling Multiple Suggestions

    When there is more than one <suggestion> tag, the `correction` attribute in the <example> tag needs to take that into account by having a logical or operator "|". That is, when a rule includes multiple <suggestion> tags, the `correction` attribute in the corresponding `<example>` tag incorporates all possible suggestions, separated by the logical OR operator. For example, notice how the multiple suggestion tags below translate to a correction attribute in the example tag with a logical or "|" operator:
    ```
    <suggestion>through <match no="5"/></suggestion>
    <suggestion>by <match no="5"/></suggestion>
    <suggestion>with <match no="5"/></suggestion>
    <suggestion>using <match no="5"/></suggestion>
    <suggestion>by using <match no="5"/></suggestion>
    <example correction="through computers|by computers|with computers|using computers|by using computers">widget accomplished it <marker>through the use of computers</marker>.</example>
    ```

    Note that the logical OR operator in the `correction` attribute of the example tag should ONLY include content of several suggestions. It does NOT (!) represent the logical OR of a pattern token. The following IS A COMMON ERROR YOU SHOULD NEVER DO:
    ```
     <pattern>
        <token>plain</token>
        <token>error</token>
        <token regexp="yes">analysis|doctrine|exception|inquiry|standard|test</token>
    </pattern>
    <suggestion>plain-error <match no="3"/></suggestion>    
    <example correction="plain-error analysis|plain-error doctrine|plain-error exception|plain-error inquiry|plain-error standard|plain-error test">The third prong of the Carines <marker>plain error standard</marker> is good law.</example>
    ```
    The correct <example> tag for this pattern and suggestion is:
    ```
    <pattern>
        <token>plain</token>
        <token>error</token>
        <token regexp="yes">analysis|doctrine|exception|inquiry|standard|test</token>
    </pattern>
    <suggestion>plain-error <match no="3"/></suggestion>    
    <example correction="plain-error standard">The third prong of the Carines <marker>plain error standard</marker> is good law.</example>
    ```

    ### Example tags associated with antipatterns 
    
    These tags contain neither a correction attribute, nor do they contain marker tags. When adding a new antipattern, add a new example for the newly added antipattern, and insert it after all other existing examples above the closing </rule> tag.   

    NOTE: If you modify an antipattern, do not modify any examples corresponding to patterns (i.e. example tags contain a correction attribute)

    ### Dynamic <match> tags in suggestions 

    Sometimes you will see a `match` tag inside a suggestion. These match tags have a numeric `no` attribute. The `no` attribute indicates what token (in the pattern) must be inserted in that location in the corresponding example. For example, notice how <match no="2"> causes the example tag to slot in the second word "used" in the corrected example. 
    ```
    <pattern>
        <token>presently</token>
        <token>used</token>
    </pattern>
    <suggestion>now <match no="2"/></suggestion>
    <example correction="now used">The property is <marker>presently used</marker> for a different purpose.</example>
    ```


    ## Additional Attributes

    Correct use of attributes for the token and exception tags:
    - The postag_regexp="yes" attribute should only be applied if there are multiple postags as regexp options, or if there is at least one open postag like V.*? or N.*?
    - For the inflection attribute, if there are multiple regexp options or exceptions with an inflection attribute, there needs to be both an inflected="yes" AND a regexp="yes" attribute in the opening tag of that token/exception
    
    
    ## Short tag

    Never modify <short> tags

    ## Message tag 
    
    Never modify <message> tags

    
    ## Formatting:

    ### Order
    The elements in the modified rule need to be in the following order: 
    1. <rule(…)> (rule opening tag)
    2. <antipattern>(tokens)</antipattern> (all antipatterns one after another)
    3. <pattern>tokens</pattern> (pattern)
    4. <message>(...)</message> (message)
    5. <suggestion>(...)</suggestion> (all suggestions one after another)
    6. <short>(...)</short> (short)
    7. <example correction=”(...)”>(...)</example> (example for the pattern)
    8. <example>(...)</example> (all examples for antipatterns one after another)
    9. </rule> (closing rule tag)
    

    ### Antipattern formatting 
    - All antipatterns need to be located below the '<rule>' opening tag and above the '<pattern>' opening tag within the xml rule. 
    - In case the xml rule provided already contains one or more antipattern(s), count top down and insert the new antipattern into the rule at the specified position.

    ### Token Formatting

    - The `<token>` tag can contain several attributes that further specify the kind of text it should match:
        - `regexp`: When set to "yes", this indicates that the content of the `<token>` is a regular expression. Regular expressions allow for matching patterns within text, rather than exact word matches.
        - `postag`: Specifies the part of speech that the token should match, using a code (e.g., RB for adverbs). This is useful for matching words based on their grammatical role in a sentence. More on postags below.
        - `postag_regexp`: When set to "yes", indicates that the `postag` attribute itself is a regular expression, allowing for matching multiple parts of speech.
        - `case_sensitive`: Indicates whether the match should be case-sensitive. When set to "yes", the token will only match text with the exact case specified.
        - `min`: Specifies the minimum number of times a token must appear.
        - `skip`: Allows for a certain number of tokens to be skipped in the pattern matching process. This is useful for matching patterns with variable elements in between.

    ### Exception Formatting

    - `<exception>` tags are always nested within `<token>` tags.
    - They can contain attributes similar to `<token>`, such as `regexp` for regular expressions, allowing for precise definition of exceptions.
    - Exceptions do not have their own content but modify the match behavior of their parent `<token>`.

    ### Additional formatting
    - Remove all ',' symbols following the 'BRIEFCATCH_`number`', the 'BRIEFCATCH_`CATEGORYNAME`_`number`', the '</pattern>', each '</suggestion>, '</message>', and '</example>' object in the code provided in the input. 
    - Do not delete any other ',' symbols in the code other than the ones specifically listed in the before sentence. 
    - Delete all spaces preceding or succeeding any "<" and ">" symbols in the code.

    
    ## Examples of valid XML rules

    Below are a few examples of valid rules:

    <rule id="BRIEFCATCH_5990191730927097327234561913918938571" name="BRIEFCATCH_PUNCHINESS_575">
        <antipattern>
            <token>for</token>
            <token min="0" regexp="yes">clear|flagrant|blatant</token>
            <token regexp="yes">violation|violations</token>
            <token>of</token>
            <token regexp="yes">a|his|these|an|this|local</token>
        </antipattern>
        <pattern>
            <token>for</token>
            <token min="0" regexp="yes">clear|flagrant|blatant</token>
            <token regexp="yes">violation|violations</token
            ><token>of</token>
        </pattern>
        <suggestion>for violating</suggestion>
        <example correction="for violating">The ordinance allowed the prosecutions <marker>for violations of</marker> the local laws.</example>
        <example>He was arrested for clear violations of local law.</example>
    </rule> 

    <rule id="BRIEFCATCH_40121849758005575304977819230225859512" name="BRIEFCATCH_LEGALESE_20271">
        <antipattern>
            <token>in</token>
            <token>cases</token>
            <token>where</token>
            <token>the</token>
            <token regexp="yes">alleged|amount|appellant|appellee|applicant|child|claimant|court|courts|data|defendant|parties|patient|person|petitioner|plaintiff|respondent|state|victim</token>
        </antipattern>
        <pattern>
            <token>in</token>
            <token>cases</token>
            <token>where</token>
        </pattern>
        <suggestion>when</suggestion>
        <example correction="When"><marker>In cases where</marker> evidence is insufficient, the case may be dismissed.</example><example>In cases where the alleged data is insufficient, the case may be dismissed.</example>
    </rule>

    <rule id="BRIEFCATCH_46715561881831052155723024309968518543" name="BRIEFCATCH_PUNCTUATION_191">
        <pattern>   
            <token case_sensitive="yes">non-profit</token>
        </pattern>
        <suggestion>nonprofit</suggestion>
        <example correction="nonprofit">The <marker>non-profit</marker> corporation was audited.</example>
    </rule>

    <rule id="BRIEFCATCH_81799141988807509754312103338977213148" name="BRIEFCATCH_CONCISENESS_4863">
        <pattern>
            <token>through</token>
            <token>the</token>
            <token>use</token>
            <token>of</token>
            <token regexp="yes">[A-Za-z]+<exception>force</exception></token>
        </pattern>
        <suggestion>through <match no="5"/></suggestion>
        <suggestion>by <match no="5"/></suggestion>
        <suggestion>with <match no="5"/></suggestion>
        <suggestion>using <match no="5"/></suggestion>
        <suggestion>by using <match no="5"/></suggestion>
        <example correction="through computers|by computers|with computers|using computers|by using computers">widget accomplished it <marker>through the use of computers</marker>.</example>
        <example>The plaintiff alleges the defendant only achieved this result <marker>through the use of force</marker>.</example>
    </rule>
    

    # PART II: Interpreting Modification Instructions

    The previous section provides instructions for how to make valid xml rules. This part will describe how you should update the provided rule using user instructions. When updating rules, it is critically important that the restrictions described above are respected. 
    
    The user will provide you with an original rule "Original Rule", the element of the rule that needs to be modified " Element type to modify", the modification action "Action to take with this element" and an instruction for how to modify the element "Specific Modifications". Your task is to apply the requested modification to the original rule. 


    ## Specific Modifications

    If asked to change a token, you may need to replace the original token specified in order for the change to be correct. The original element you are replacing should not effect how you generate a new one.

    - Regular Words: If a single word is by itself and not in a (parenthesis), then this is an individual token. 
    - If a set of words surrounded by parenthesis is given, then this token is a regular expression token that should contain all of the words within the parenthesis, with each separated by a "|" character. For example, the instructions `(very simple obvious) fact that` corresponds to the following tokens:
    ```
    <token regexp="yes">very|simple|obvious</token>
    <token>fact</token>
    <token>that</token>
    ```
    - Tokens can have part-of-speech tags
    

    ## Operators: `!`,`~`,`/`

    - an exclamation mark `!` indicates that token should be part of an exception 
    - a tilde `~` indicates that the `min` attribute of that token needs to be added like so `min="0"` in the opening tag of that token tag in the output. That is, if the action provided by the user has a tilde (~) symbol, you must add to the corresponding token the attribute `min="0"`.
    - a forward slash `/` indicates that the word should be case sensitive. By default case_sensitive="no", if the token needs to be case_sensitive="yes," this will be requested by putting a "/" character before the word whose token should have the case_sensitive="yes" attribute

    
    {replace_rx}

    {replace_ct}

    {replace_casesens}

    ## Examples 

    Below are a series, delimited by tripple equal signs (===), of examples of user inputs and expected outputs.

    ===

    # Original Rule:
    <rule id="BRIEFCATCH_232392047072038456938986019050228512304" name="BRIEFCATCH_PUNCHINESS_932">
        <antipattern>
            <token>requires</token>
            <token>further</token>
            <token>proof</token>
        </antipattern>
        <pattern>
            <token>require</token>
            <token>proof</token>
        </pattern>
        <suggestion><match no="1"/> more <match no="2"/></suggestion>
        <example>The parties requires further proof on this point.</example>
        <example correction="require more proof">The parties will be able to <marker>require proof</marker> on this point.</example>
    </rule>
    
    # Element:
    Pattern

    # Specific modification:
    'change first token to: (CT(require) !requiring)'

    # Modified Rule:
    <rule id="BRIEFCATCH_232392047072038456938986019050228512304" name="BRIEFCATCH_PUNCHINESS_932">
        <antipattern>
            <token>requires</token>
            <token>further</token>
            <token>proof</token>
        </antipattern>
        <pattern>
            <token inflected="yes">require
                <exception>requiring</exception>
            </token>
            <token>proof</token>
        </pattern>
        <suggestion><match no="1"/> more <match no="2"/></suggestion>
        <example>The parties requires further proof on this point.</example>
        <example correction="require more proof">The parties will be able to <marker>require proof</marker> on this point.</example>
    </rule>
    
    ===

    # Original Rule:
    <rule id="BRIEFCATCH_232392047072038456938986019050228512304" name="BRIEFCATCH_PUNCHINESS_932">
        <pattern>
            <or>
                <token inflected="yes">inquire</token>
                <token>inquiry</token>
            </or>
            <token>as</token>
            <token>to</token>
        </pattern>
        <suggestion><match no="1"/> into</suggestion>
        <suggestion><match no="1"/> about</suggestion>
        <example correction="inquiry into|inquiry about">The <marker>inquiry as to</marker> the strong majority of documents and testimony sought continues.</example>
    </rule>

    # Element:
    Pattern

    # Specific modification:
    add final token: ( RX(.*? ) !which !where !how !when )

    # Modified Rule:
    <rule id="BRIEFCATCH_232392047072038456938986019050228512304" name="BRIEFCATCH_PUNCHINESS_932">
        <pattern>
            <or>
                <token inflected="yes">inquire</token>
                <token>inquiry</token>
            </or>
            <token>as</token>
            <token>to</token>
            <token>
                <exception regexp="yes">which|where|how|when</exception>
            </token>
        </pattern>
        <suggestion><match no="1"/> into</suggestion>
        <suggestion><match no="1"/> about</suggestion>
        <example correction="inquiry into|inquiry about">The <marker>inquiry as to the</marker> strong majority of documents and testimony sought continues.</example>
    </rule>

    ===

    # Original Rule:
    <rule id="BRIEFCATCH_14245065389327423897492387493287498237949" name="BRIEFCATCH_PUNCHINESS_382">
        <pattern>
            <token>presently</token>
            <token postag="VBN"/>
        </pattern>
        <suggestion><match no="2"/></suggestion>
        <suggestion>now <match no="2"/></suggestion>
        <example correction="used|now used">The property is <marker>presently used</marker> for a different purpose.</example>
    </rule> 

    # Element:
    Antipattern

    # Specific modification:
    add antipattern for: presently ( N.*? !all !are !being !beliefs !due !even !fails !having !his !hold)

    # Modified rule:
    <rule id="BRIEFCATCH_14245065389327423897492387493287498237949" name="BRIEFCATCH_PUNCHINESS_382">
        <pattern>
            <token>presently</token>
            <token postag="VBN"/>
        </pattern>
        <antipattern>
            <or> 
                <token postag_regexp="yes" postag="N.*?"/> 
                <token regexp="yes">all|are|being|beliefs|due|even|fails|having|his|hold</token> 
            </or>
        </antipattern>
        <suggestion><match no="2"/></suggestion>
        <suggestion>now <match no="2"/></suggestion>
        <example correction="used|now used">The property is <marker>presently used</marker> for a different purpose.</example>
        <example>It is unclear whether presently he will commit.</example>
    </rule> 

    ===

    <rule id="BRIEFCATCH_189790299448848023027828356741690043135" name="BRIEFCATCH_PUNCHINESS_436">
        <pattern>
            <token>in</token>
            <token>so</token>
            <token>far</token>
            <token>as</token>
        </pattern>
        <suggestion>because</suggestion>
        <suggestion>given that</suggestion>
        <suggestion>if</suggestion>
        <example correction="because|given that|if">We defer to the discretion of the court <marker>in so far as</marker> it’s bottomed on the claim.</example>
    </rule>
   
    # Element:  
    Antipattern
    
    # Specific modification:
    Add antipattern for: ( and that ) in so far as

    # Modified rule:
    <rule id="BRIEFCATCH_189790299448848023027828356741690043135" name="BRIEFCATCH_PUNCHINESS_436">
        <antipattern>
            <token regexp="yes">and|that</token>
            <token>in</token>
            <token>so</token>
            <token>far</token>
            <token>as</token>
        </antipattern>
        <pattern>
            <token>in</token>
            <token>so</token>
            <token>far</token>
            <token>as</token>
        </pattern>
        <suggestion>because</suggestion>
        <suggestion>given that</suggestion>
        <suggestion>if</suggestion>
        <example correction="because|given that|if">We defer to the discretion of the court <marker>in so far as</marker> it’s bottomed on the claim.</example>
        <example>We are done here such that in so far as the claim is bottomed we can proceed</example>
    </rule>
    """


# POS TAG ANALYSIS


def get_generalized_pos_tags(input_str) -> Dict[str, str]:
    # get generalized pos tags (e.g. N.*?)
    regex_in_specific_actions = [r"N\.\*\?"]
    pattern = r"|".join(regex_in_specific_actions)
    generalized_pos_tags = re.findall(pattern, input_str)

    def get_base_of_pos_tag(generalized_pos_tag):
        # NOTE: this might expand if we start working with more types of generalized pos tag
        return generalized_pos_tag.replace(".*?", "")

    # make them into base form and collect
    matching_tags = {}
    for tag in generalized_pos_tags:
        base_form = get_base_of_pos_tag(tag)
        for pos_key in POS_MAPS:
            if pos_key.startswith(base_form):
                matching_tags[pos_key] = POS_MAPS[pos_key]
    return matching_tags


def get_simple_pos_tags(input_str):
    matching_tags = {}
    for pos_tag in POS_MAPS.keys():
        if pos_tag in input_str:
            matching_tags[pos_tag] = POS_MAPS[pos_tag]
    return matching_tags


def get_fewshot_pos(pos: List, target_element: str):
    """
    TODO: this function should analyze what pos tags are provided as inputs and select the appropriate examples.
    """
    if target_element not in ["pattern", "antipattern"]:
        print(
            "expected target element to be either pattern or antipattern, but got",
            target_element,
        )
    return f"""
    Example Input: I like to VB
    Expected Output:
    <{target_element}>
    <token>I</token>
    <token>like</token>
    <token>to</token>
    <token postag=”VB”/>
    </{target_element}>

    Example Input: I like ( NNP NNS )
    Expected Output:
    <{target_element}>
    <token>I</token>
    <token>like</token>
    <postag_regexp="yes" postag="NNP|NNS"/>
    </{target_element}>

    Example Input: I like N.*
    Expected Output:
    <{target_element}>
    <token>I</token>
    <token>like</token>
    <token postag_regexp="yes" postag="N.*">
    </{target_element}>
    """


# OTHER TAGS


def has_tilde(s):
    return "~" in s


def has_ct(s):
    return "CT(" in s


def has_rx(s):
    return "RX(.*?)" in s


def has_casesens(s):
    return "/" in s


def has_backslash_number(s):
    return "\<number>" in s


def has_sent_start(s):
    return "sent_start" in s.lower()


# main

ANTIPATTERN_INSTRUCTIONS = CT_TAG_INSTRUCTIONS = SUGGESTION_AND_EXAMPLE_INSTRUCTIONS = (
    SENT_START_INSTRUCTIONS
) = ""


def get_dynamic_standard_prompt(
    original_rule, target_element, element_action, specific_actions
):
    # POS tags are required
    pos_tags_in_specific_actions = {
        **get_simple_pos_tags(specific_actions),
        **get_generalized_pos_tags(specific_actions),
    }
    pos_tags_in_rule = get_pos_tag_dicts_from_rule(original_rule)
    all_pos_tags = {**pos_tags_in_rule, **pos_tags_in_specific_actions}
    # format prompt
    _replace_pos_tags = "\n".join(f"{k} = {v}" for k, v in all_pos_tags.items())
    _replace_pos_tags_fewshot_examples = get_fewshot_pos(
        pos_tags_in_specific_actions, target_element
    )
    _replace_antipattern = (
        ANTIPATTERN_INSTRUCTIONS if target_element == "antipattern" else ""
    )

    _replace_backslash_number = SUGGESTION_AND_EXAMPLE_INSTRUCTIONS

    SUGGESTION_AND_EXAMPLE_INSTRUCTIONS
    _replace_sent_start = (
        SENT_START_INSTRUCTIONS
        if has_sent_start(specific_actions + original_rule)
        else ""
    )
    replace_rx = RX_PROMPT if has_rx(specific_actions) else ""
    replace_ct = CT_PROMPT if has_ct(specific_actions) else ""
    replace_casesens = CASESENS_PROMPT if has_casesens(specific_actions) else ""
    return format_optimized_standard_prompt(replace_rx, replace_ct, replace_casesens)

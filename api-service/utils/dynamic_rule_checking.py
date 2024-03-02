import re
from typing import Dict, List, Tuple
from domain.dynamic_prompting.parts_of_speech import POS_MAPS
from domain.dynamic_prompting.prompt_leggo import (
    VALIDATE_RULE_PROMPT,
    REGEX_INSTRUCTIONS_PROMPT,
)
from utils.dynamic_prompting import (
    get_pos_tag_dicts_from_rule,
    remove_message_and_short_tags,
    rule_has_regex,
    replace_all_instances_of_tag,
)
from utils.logger import setup_logger
from utils.regexp_validation import post_process_xml
from utils.rule_similarity import get_similar_template_rules
from utils.utils import (
    call_gpt_with_backoff,
    generate_simple_message,
    remove_thought_tags,
)


dynamic_logger = setup_logger(__name__)

PROMPT = """
You are a component in a system designed to validate xml content. The xml content you will be validating encodes the rules for a software designed to make text edits. Below are instructions on how the xml is supposed to be structured. These instructions are formatted as a markdown document. 

# PART I: XML Rules

## Introduction

The following are the most important tags:

- `<rule>`: this is the parent tag for a rule
- `<pattern>`: this encloses a series of token tags, and encodes the snippets of text that the software is looking out for in order to get replaced. Patterns are made of tokens and exceptions.
- `<antipattern>`: this also encloses a series of token tags, and also encodes the snippets of text that the software is looking out. However, unlike <patterns> which get replaced, antipatterns are not replaced. 
- `<token>`: a token inside a `<pattern>` tag encodes a token of text. This can either be an entire word, a part-of-speech (POS), or a regular expression (more on these below).
- `<excetion>`: you will sometimes see exception tags inside token tags. These represent exceptions to the token that should not be matched by that pattern.
- `<suggestion>`: every pattern and antipattern has one and only one corresponding suggestion tag. Suggestion tags represent the text that the software will suggest as a replacement for the pattern encoded by that rule. 
- `<example>`: every pattern and antipattern have a corresponding example tag that exemplifies a snippet of text where that would trigger that pattern or antipattern. More on example tags below. 
- `<short>`: You do not need to touch these. Just copy verbatim.
- `<message>`: You do not need to touch these. Just copy verbatim.

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

Your GOAL will be to ensure the <example> tag is valid according to the rules described below.

## Pattern <pattern> tags

Patterns represent text that is supposed to be replaced. They are composed of <token> tags described below. 

Every pattern is associated with an <example> tag. Example tags associated with patterns must have a correction attribute and a marker tag (both are described below). 

## Antipattern <antipattern> tags 

Antipatterns represent text that is not supposed to be replaced. Antipatterns begin and end with their tags on separate lines. Like pattern tags, they are also composed of <token> tags. 

Every antipattern is also associated with a corresponding <example> tag. Unlike example tags associated with patterns, the example tags associated with antipatterns must not contain a correction attribute nor marker tags.


## Token <token> tags 

Patterns and antipatterns are defined by tokens. Tokens are encoded by <token> tags. These define the specific elements within patterns and antipatterns that the software should identify. They can match specific words, parts of speech, or regular expressions. 

Importantly, tokens can contain `<exception>` tags. These define specific words or patterns that should not be matched by the token, even if they fit the other criteria specified.


## Logical OR operator

Tokens may contain a logical OR operator, signified by a pipe symbol "|". This allows the tag to match multiple words. For example, the following tokens:
```
<token>assisted</token>
<token regexp="yes">in|with</token>
```
match either "assisted in" or "assisted with" substrings.


## Suggestion <suggestion> tags

Suggestion tags are central to the system. Above we described <pattern> and <token> tags, and how they find matching expressions in a text segment. Suggestion tags encode how the text segment that matches the pattern should be modified. For example, the following xml instructs the program to find occurences of the substring "file a motion seeking to" and replace those with the substring "move to".

```
<pattern>
    <token>file</token>
    <token>a</token>
    <token>motion</token>
    <token>seeking</token>
    <token>to</token>
</pattern>
<suggestion>move to</suggestion>
```

This way, suggestion tags provide the text that will replace the matched pattern. 

Critically important: You will rarely have to modify suggestion tags. ONLY MODIFY SUGGESTION TAGS WHEN EXPLICITLY REQUESTED TO DO SO.

### Dynamic <match> tags in suggestions 

The <suggestion> tags often utilize dynamic elements to construct their recommendations based on the specific content matched by the <pattern>. These dynamic elements are captured by <match> tags. Match tags contain a `no` attribute which points to one of the <token> tags in the matched pattern. We can modify the above example and get the same effect by using <match> tags: 

```
<pattern>
    <token>file</token>
    <token>a</token>
    <token>motion</token>
    <token>seeking</token>
    <token>to</token>
</pattern>
<suggestion>move <match no="5"></suggestion>
```

This preceding xml would still find occurences of the substring "file a motion seeking to" and replace those with the substring "move to". The <match no="5"> tells the program to insert in its location the fifth token in the pattern. 


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


## Example <examaple> tags

The example tag is the most important tag for you to understand. Example tags demonstrate the practical application of rules, showing a before-and-after view of the text. Your job will be to ensure these tags are validated appropriately. As alluded to above, there are two types of example tags, those associated with patterns, and those associated with antipatterns.

Critically improtant: Every pattern and antipattern in the rule should have ONE AND ONLY ONE corresponding example tag! 
    
### Pattern <example> tags

Every pattern is associated with an <example> tag. Example tags associated with patterns must have a correction attribute and a marker tag: `<example correction="...">This is <marker>the text</marker> to be replaced.` 

- The example tag associated with a pattern must have <marker>...</marker> tags surrounding the specific text enclosed by the example tag that matches the corresponding pattern.
- The example tag associated with patterns must have a correction attribute. This correction attribute indicates what the text that matches the pattern should be corrected to. The corrections are given by the suggestion tags in the rule. 

```
<pattern>
    <token>consulted</token>
    <token>with</token>
</pattern>
<suggestion><match no="1"/></suggestion>
<example correction="consulted">The expert <marker>consulted with</marker> the lawyer.</example>
```

```
<pattern>
    <token>does</token>
    <token>not</token>
    <token>fall</token>
    <token regexp="yes">inside|within</token>
</pattern>
<suggestion>falls outside</suggestion>
<example correction="falls outside">Respondent’s scheme <marker>does not fall within</marker> the definition.</example>
```

<example> tags associated with patterns work in tandem with <suggestion> tags to provide recommendations for improving text. Example tags shows how to apply suggestions to the matched pattern and through the `correction` attribute of the `example` tag shows the effect of each suggestion on the substring within the <marker> tags of the matched pattern. 


### Antipattern <example> tags

Every antipattern is also associated with a corresponding <example> tag. Unlike example tags associated with patterns, the example tags associated with antipatterns must not contain a correction attribute nor marker tags.

- An example tag associated with an antipattern should not have any attributes and should not have marker tags. They provide an example of text that is captured by the tokens of the antipattern and therefore does not need to be corrected.

```
<antipattern>
    <token postag="MD"/>
    <token>not</token>
    <token>likely</token>
</antipattern>
<antipattern>
    <token>not</token>
    <token>likely</token>
    <token>to</token>
    <token regexp="yes">prevail|succeed</token>
</antipattern>
<antipattern>
    <token>not</token>
    <token>likely</token>
    <token>to</token>
    <token>succeed</token>
</antipattern>
<pattern>
    <token>not</token>
    <token>likely</token>
    <token>
        <exception>to</exception>
    </token>
</pattern>
<suggestion>unlikely <match no="3"/></suggestion>
<example correction="unlikely that">it was <marker>not likely that</marker></example>
<example>investigation into one claim would not likely lead to investigation</example>
<example>The plaintiffs not likely to prevail on a NEPA claim.</example>
<example>They are not likely to succeed.</example>
```


### Further details on example tags associated with patterns

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

# PART II: YOUR TASK

The user will provide you with a rule xml. Your task is to evaluate whether this rule xml follows the principles established above. 

Your response should contain two parts. In the first part include your thoughts and comments around <thoughts>...</thoughts> tags. Answer the following questions:
- How many patterns does this rule have?
- How many example tags corresponding to patterns does this rule have? This number should match the number of patterns.
- How many antipatterns does this rule have?
- How many example tags corresponding to antipatterns does this rule have? This number should match the number of antipatterns
- Do the <marker>...</marker> tags in the example tags span the section of text represented by the pattern?
- How many suggestion tags does this rule have?
- Are all suggestion tags represented in the correction field of the example tags?

If the rule xml meets all the criteria established in 'PART I XML Rules', you should respond back with the same string provided to you. 

If the rule xml violates the criteria established in 'PART I XML Rules', you should respond back with the corrected version of the rule xml.

You are part of a larger software system. Your output will directly effect the user view. Therefore you must not include additional comments. Your output SHOULD ALWAYS begin with "<rule" substring and end with "</rule>" substring.

You will also see <short> and <message> tags. Just copy paste these from the input to the output. You should never modify these. 

## Few shot examples:

User: 
<rule id="BRIEFCATCH_326463179224822017023863994110462000611" name="BRIEFCATCH_PUNCTUATION_198">
    <pattern>
        <token>good</token>
        <token>faith</token>
        <token regexp="yes">attempt|bargaining|belief|doubt|effort|exception|negotiations|purchaser</token>
    </pattern>
    <message>If this phrase modifies the noun that follows, consider hyphenating it for clarity.|**Example** from Justice Gorsuch: “[S]ome courts proceeding before the 1905 Act . . . rarely authorized profits for purely **good-faith infringement**.”|**Example** from Justice Kagan: “Those differences make judicial review of the . . . duty of **good-faith bargaining** a poor model . . . .”|Learn more about hyphenation [here](https://briefcatch.com/lessons/punctuation-hyphenation/).</message>
    <suggestion>good-faith <match no="3"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":true,"isStyle":true,"correctionCount":1,"priority":"3.277","WORD":true,"OUTLOOK":true}</short>
    <example correction="good-faith attempt">They’re <marker>good faith attempt</marker>.</example>
    <example correction="good-faith bargaining">They’re <marker>good faith bargaining</marker>.</example>
    <example correction="good-faith belief">They’re <marker>good faith belief</marker>.</example>
    <example correction="good-faith doubt">They’re <marker>good faith doubt</marker>.</example>
    <example correction="good-faith effort">They’re <marker>good faith effort</marker>.</example>
    <example correction="good-faith exception">They’re <marker>good faith exception</marker>.</example>
    <example correction="good-faith negotiations">They’re <marker>good faith negotiations</marker>.</example>
    <example correction="good-faith purchaser">They’re <marker>good faith purchaser</marker>.</example>

Assistant:
<thought>[`insert your reasoning about the correctness of this rule here`]</thought>
<rule id="BRIEFCATCH_326463179224822017023863994110462000611" name="BRIEFCATCH_PUNCTUATION_198">
    <pattern>
        <token>good</token>
        <token>faith</token>
        <token regexp="yes">attempt|bargaining|belief|doubt|effort|exception|negotiations|purchaser</token>
    </pattern>
    <message>If this phrase modifies the noun that follows, consider hyphenating it for clarity.|**Example** from Justice Gorsuch: “[S]ome courts proceeding before the 1905 Act . . . rarely authorized profits for purely **good-faith infringement**.”|**Example** from Justice Kagan: “Those differences make judicial review of the . . . duty of **good-faith bargaining** a poor model . . . .”|Learn more about hyphenation [here](https://briefcatch.com/lessons/punctuation-hyphenation/).</message>
    <suggestion>good-faith <match no="3"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":true,"isStyle":true,"correctionCount":1,"priority":"3.277","WORD":true,"OUTLOOK":true}</short>
    <example correction="good-faith attempt">They’re <marker>good faith attempt</marker>.</example>

User:
<rule id="BRIEFCATCH_322580514589798171215317472742154216778" name="BRIEFCATCH_USAGE_45">
    <pattern>
        <token>preventative</token>
        <token regexp="yes">action|and|care|detention|health|maintenance|measure|measures|medicine|services</token>
    </pattern>
    <message>**Preventive** is the preferred form.|**Example** from Justice Sotomayor: “Whether the Fourth Amendment permits the pretextual use of a material witness warrant for **preventive** detention of an individual whom the Government has no intention of using at trial is . . . a closer question than the majority’s opinion suggests.”|**Example** from David Frederick: “New Hampshire has looked at problems with local access to medical services, while Utah uses its data to study **preventive** care.”|**Example** from The 9-11 Report: “We want to ensure that the Bureau’s shift to a **preventive** counterterrorism posture is more . . . .”</message>
    <suggestion>preventive</suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":true,"isStyle":true,"correctionCount":1,"priority":"1.40","WORD":true,"OUTLOOK":true}</short>
    <example correction="preventive">I like <marker>preventative</marker> medicine.</example>
</rule>

Assistant:
<thought>[`insert your reasoning about the correctness of this rule here`]</thought>
<rule id="BRIEFCATCH_322580514589798171215317472742154216778" name="BRIEFCATCH_USAGE_45">
    <pattern>
        <token>preventative</token>
        <token regexp="yes">action|and|care|detention|health|maintenance|measure|measures|medicine|services</token>
    </pattern>
    <message>**Preventive** is the preferred form.|**Example** from Justice Sotomayor: “Whether the Fourth Amendment permits the pretextual use of a material witness warrant for **preventive** detention of an individual whom the Government has no intention of using at trial is . . . a closer question than the majority’s opinion suggests.”|**Example** from David Frederick: “New Hampshire has looked at problems with local access to medical services, while Utah uses its data to study **preventive** care.”|**Example** from The 9-11 Report: “We want to ensure that the Bureau’s shift to a **preventive** counterterrorism posture is more . . . .”</message>
    <suggestion>preventive</suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":true,"isStyle":true,"correctionCount":1,"priority":"1.40","WORD":true,"OUTLOOK":true}</short>
    <example correction="preventive">I like <marker>preventative medicine</marker>.</example>
</rule>

User:
<rule id="BRIEFCATCH_86869803831870490687851873429223778199" name="BRIEFCATCH_PUNCTUATION_197">
    <pattern>
        <token>plain</token>
        <token>error</token>
        <token regexp="yes">analysis|doctrine|exception|inquiry|standard|test</token>
    </pattern>
    <message>If this phrase modifies the noun that follows, consider hyphenating it for clarity.|**Example** from Justice Scalia: “The real question in this case is not whether **plain-error review** applies when a defendant fails to preserve a claim . . . .”|Learn more about hyphenation [here](https://briefcatch.com/lessons/punctuation-hyphenation/).</message>
    <suggestion>plain-error <match no="3"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":true,"isStyle":true,"correctionCount":1,"priority":"3.2390","WORD":true,"OUTLOOK":true}</short>
    <example correction="plain-error analysis|plain-error doctrine|plain-error exception|plain-error inquiry|plain-error standard|plain-error test">The third prong of the Carines <marker>plain error standard</marker> is good law.</example>
</rule>

Assistant:
<thought>[`insert your reasoning about the correctness of this rule here`]</thought>
<rule id="BRIEFCATCH_86869803831870490687851873429223778199" name="BRIEFCATCH_PUNCTUATION_197">
    <pattern>
        <token>plain</token>
        <token>error</token>
        <token regexp="yes">analysis|doctrine|exception|inquiry|standard|test</token>
    </pattern>
    <message>If this phrase modifies the noun that follows, consider hyphenating it for clarity.|**Example** from Justice Scalia: “The real question in this case is not whether **plain-error review** applies when a defendant fails to preserve a claim . . . .”|Learn more about hyphenation [here](https://briefcatch.com/lessons/punctuation-hyphenation/).</message>
    <suggestion>plain-error <match no="3"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":true,"isStyle":true,"correctionCount":1,"priority":"3.2390","WORD":true,"OUTLOOK":true}</short>
    <example correction="plain-error standard">The third prong of the Carines <marker>plain error standard</marker> is good law.</example>
</rule>

User:
<rule id="BRIEFCATCH_72217380358443072298334619098248039878" name="BRIEFCATCH_PUNCHINESS_921">
    <antipattern>
        <token inflected="yes">call</token>
        <token>upon</token>
        <token regexp="yes">a|all|his|me|the</token>
    </antipattern>
    <pattern>
        <token inflected="yes">call</token>
        <token>upon</token>
    </pattern>
    <message>Would shorter words add punch?|**Example** from Justice Gorsuch: “When **called on** to interpret a statute, this Court generally seeks to discern and apply the ordinary meaning of its terms at the time of their adoption.”|**Example** from Deanne Maynard: “The [order] merely confirms that it was not until later proceedings that he was **called on** to single out these waters.”</message>
    <suggestion><match no="1"/> on</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">ask</match></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":2,"priority":"2.84","WORD":true,"OUTLOOK":true}</short>
    <example correction="called on|asked">She was <marker>called upon</marker> three times.</example>
</rule>

Assistant:
<thought>[`insert your reasoning about the correctness of this rule here`]</thought>
<rule id="BRIEFCATCH_72217380358443072298334619098248039878" name="BRIEFCATCH_PUNCHINESS_921">
    <antipattern>
        <token inflected="yes">call</token>
        <token>upon</token>
        <token regexp="yes">a|all|his|me|the</token>
    </antipattern>
    <pattern>
        <token inflected="yes">call</token>
        <token>upon</token>
    </pattern>
    <message>Would shorter words add punch?|**Example** from Justice Gorsuch: “When **called on** to interpret a statute, this Court generally seeks to discern and apply the ordinary meaning of its terms at the time of their adoption.”|**Example** from Deanne Maynard: “The [order] merely confirms that it was not until later proceedings that he was **called on** to single out these waters.”</message>
    <suggestion><match no="1"/> on</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">ask</match></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":2,"priority":"2.84","WORD":true,"OUTLOOK":true}</short>
    <example correction="called on|asked">She was <marker>called upon</marker> three times.</example>
    <example>When she called upon his parents, they did not answer.</example>
</rule>
"""


def check_rule_modification(rule_xml):
    response, usage = call_gpt_with_backoff(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": rule_xml},
        ],
        temperature=0,
        max_length=1500,
    )
    response = response.replace("```xml", "")
    response = response.replace("```", "")
    response = response.replace("N.*?", "N.*")
    rule_xml = re.findall(r"<rule.*?</rule>", response, re.DOTALL)[0]
    # return response, rule_xml

    return rule_xml, [usage]

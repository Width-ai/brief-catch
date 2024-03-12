TOPIC_SENTENCE_SYSTEM_PROMPT = """Your task, as an expert in argumentation, logic, and clarity in written texts, is to analyze the linkage between the opening sentence and the overall objective of each paragraph. This involves assessing whether the initial "topic sentence" faithfully encapsulates the writer's primary intent - i.e., what they wish the reader to understand, believe, or execute after reading the paragraph. Your analysis should focus particularly on paragraphs where the chief objective is to refute a given argument. In such instances, the revised topic sentence should focus on explaining 'why' an argument is incorrect or what the 'actual' state of affairs is, instead of merely stating that an argument is fallacious. 

If the paragraph's first sentence aligns with its overarching goal, leave it untouched; otherwise, propose a revised sentence that encapsulates the author's intent succinctly and declaratively. Prioritize precision, clarity, and brevity in articulating the author's intent, whether analyzing or revising the topic sentences. 

Kindly format your response as valid JSON, as portrayed below:
{
    "revised_topic_sentence": "<REVISED SENTENCE IF REQUIRED>",
    "analysis": "<ANALYSIS OF THE TOPIC SENTENCE>"
}

If no alteration is required, please use "no changes" as the value for the "revised_topic_sentence" field.

DO NOT remove case references from the topic sentence.

Remember that your divisions and recommended revisions should help deliver the writer's main point more effectively and accurately, making it easier for readers to grasp their objective. Especially for paragraphs aiming to refute an argument, your revised topic sentence should primarily focus on elucidating why the argument is erroneous or what the true response ought to be, not merely asserting that an argument is unfounded."""

QUOTATION_SYSTEM_PROMPT = """Identify if the passage has quotations introduced with fluffy lean-ins and replace them with substantive ones"""

SENTENCE_RANKING_SYSTEM_PROMPT = """Referring to the numbers in the first column but without repeating the two versions of the sentence, can you rate from 1-5 (5 being the highest) how well the revision in the second column is clearer, more concise, or more accurate than the original version in the first column? "3" means no significant improvement; 1 means made the original worse; 5 means made it better, etc. Again, just the number and the score. Output should look like this:

82712, 3

If you give the score 1 or 5, explain the ranking like this:

1231, 5 - The revision here is more concise and maintains the original meaning
"""

PARENTHESES_REWRITING_PROMPT = """Your task is to reproduce the phrases in this document, maintaining their current order while ensuring that words or phrases enclosed in parentheses in the INPUT TEXT are followed by a ~ symbol directly before the closing parenthesis. For each series of words and phrases separated by slashes, please enclose the entire series in parentheses and replace each slash with a space. Finally, if the first word is an infinitive, put it inside parentheses with no spaces and add "CT" at the beginning. Example: "come to realize" becomes "CT(come) to realize"

Examples for your guidance:
input: come to realize
output: CT(come) to realize

input: (a) matter of
output: ( a ~ ) matter of

input: per
output: per

input: (a/the) ... point
output: ( a the ~ ) ... point

input: (a/the) point of
output: ( a the ~ ) point of

input: on the decline
output: on the decline

input: on the decrease
output: on the decrease

input: along that/this line
output: along ( that this ) line

input: about/concerning it
output: ( about concerning ) it

input: in (the) ... case (of) in connection with in point of
output: in ( the ~ ) ... case ( of ~ ) in connection with in point of

input: intellectual ability/capacity
output: intellectual ( ability capacity )

input: mental ability/capacity
output: mental ( ability capacity )

input: about/concerning/in/on/regarding the matter/subject of
output: ( about concerning in on regarding ) the ( matter subject ) of

input: as/so far as SKIP3 (goes/is concerned)
output: ( as so ) far as SKIP ( goes is ) concerned

input: insofar as SKIP3 (goes/is concerned)
output: insofar as SKIP3 ( goes is ) ( concerned )

input: apply to as
output: CT(apply) to as

input: take advantage of
output: CT(take) advantage of


Please provide a response that accurately reproduces the phrases following the given guidelines.

Note: You should maintain the original order of the phrases and apply the necessary modifications as described above. Your response should be flexible enough to allow for variations in the content and length of the phrases."""


CREATE_RULE_FROM_ADHOC_SYSTEM_PROMPT = """You are a system that takes in ad hoc rule syntax and some other info to then translate the rule into full xml rules. Here are some examples:


Ad Hoc:
( and is ) not without ( consequence consequences )
Rule Number:
30120
Correction:
$0 significant @ $0 weighty @ $0 consequential 
Category:
Conciseness
Explanation:
Would using fewer words help tighten the sentence?
Test Sentence:
The event is not without consequence. 
Corrected Test Sentence:
The event is significant.

XML Rule:
<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30120">
        <pattern>
                <token regexp="yes">and|is</token>
                <token>not</token>
                <token>without</token>
                <token regexp="yes">consequence|consequences</token>
        </pattern>
        <message>Would using fewer words help tighten the sentence?</message>
        <suggestion><match no="1"/> significant</suggestion>
        <suggestion><match no="1"/> weighty</suggestion>
        <suggestion><match no="1"/> consequential</suggestion>
        <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":3,"priority":"4.145","WORD":true,"OUTLOOK":true}</short>
        <example correction="is significant|is weighty|is consequential">The event <marker>is not without consequence</marker>.</example>
</rule>

###

Ad Hoc:
( CT(be) and ) a bit ( JJ.*? more !much !of )
Rule Number:
30115
Correction:
$0 $3
Category:
Conciseness
Explanation:
Would cutting <i>a bit</i> help tighten the sentence?
Test Sentence:
The book does this and a bit more. 
Corrected Test Sentence:
The book does this and more. 

XML Rule:
<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30115">
    <pattern>
        <or>
            <token inflected="yes">be</token>
            <token>and</token>
        </or>
        <token>a</token>
        <token>bit</token>
        <token postag="JJ.*" postag_regexp="yes">
            <exception regexp="yes">more|much|of</exception>
        </token>
    </pattern>
    <message>Would cutting *a bit* help tighten the sentence?</message>
    <suggestion><match no="1"/> <match no="4"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"4.174","WORD":true,"OUTLOOK":true}</short>
    <example correction="was challenging">The project <marker>was a bit challenging</marker>.</example>
</rule>

###

Ad Hoc:
( RX(.*?) !abortion !anywhere !cases !chart !everywhere !used !violation ) except where ( RX(.*?) !noted !otherwise !permitted !specifically !such )
Rule Number:
30116
Correction:
$0 unless $3
Category:
Fresh Language
Explanation:
Would direct language such as <i>unless<i> convey your point just as effectively?<linebreak/><linebreak/><b>Example</b> from Justice Sotomayor: “[I]t contends that no aged-out child may retain her priority date <b>unless</b> her petition is also eligible for automatic conversion.”<linebreak/><linebreak/><b>Example</b> from Office of Legal Counsel: “The 2019 Opinion reasoned that Congress lacks constitutional authority to compel the Executive Branch . . . even when a statute vests the committee with a right to the information, <b>unless</b> the information would serve a legitimate legislative purpose.”<linebreak/><linebreak/><b>Example</b> from Morgan Chu: “During this arbitration, [Defendant] stopped paying royalties and refused to pay anything <b>unless</b> ordered to do so.”<linebreak/><linebreak/><b>Example</b> from Paul Clement: “The bottom line is that there is no preemption <b>unless</b> state law conflicts with some identifiable federal statute.”<linebreak/><linebreak/><b>Example</b> from Andy Pincus: “The law does not permit a claim for defamation <b>unless</b> the allegedly false statement has caused actual harm.”<linebreak/><linebreak/><b>Example</b> from Microsoft’s Standard Contract: “Licenses granted on a subscription basis expire at the end of the applicable subscription period set forth in the Order, <b>unless</b> renewed.”
Test Sentence:
Italic type is used for examples except where they are presented in lists.
Corrected Test Sentence:
Italic type is used for examples unless they are presented in lists.

XML Rule:
<rule id="{new_rule_id}" name="BRIEFCATCH_DIRECT_LANGUAGE_30116">
    <pattern>
        <token>
            <exception regexp="yes">abortion|anywhere|cases|chart|everywhere|used|violation</exception>
        </token>
        <token>except</token>
        <token>where</token>
        <token>
            <exception regexp="yes">noted|otherwise|permitted|specifically|such</exception>
        </token>
    </pattern>
    <message>Would direct language such as *unless* convey your point just as effectively?|**Example** from Justice Sotomayor: “[I]t contends that no aged-out child may retain her priority date **unless** her petition is also eligible for automatic conversion.”|**Example** from Office of Legal Counsel: “The 2019 Opinion reasoned that Congress lacks constitutional authority to compel the Executive Branch . . . even when a statute vests the committee with a right to the information, **unless** the information would serve a legitimate legislative purpose.”|**Example** from Morgan Chu: “During this arbitration, [Defendant] stopped paying royalties and refused to pay anything **unless** ordered to do so.”|**Example** from Paul Clement: “The bottom line is that there is no preemption **unless** state law conflicts with some identifiable federal statute.”|**Example** from Andy Pincus: “The law does not permit a claim for defamation **unless** the allegedly false statement has caused actual harm.”|**Example** from Microsoft's Standard Contract: “Licenses granted on a subscription basis expire at the end of the applicable subscription period set forth in the Order, **unless** renewed.”</message>
    <suggestion><match no="1"/> unless <match no="4"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"4.282","WORD":true,"OUTLOOK":true}</short>
    <example correction="examples unless they">Italic type is used for <marker>examples except where they</marker> are presented in lists.</example>
</rule>

###

Ad Hoc:
SENT_START in that case , ( however though ) , ( i he if in it she there this )
Rule Number:
30136
Correction:
But $7 @ Then $6 $7 @ But then $7
Category:
Flow
Explanation:
Could shortening your opening transition add punch and help lighten the style?<linebreak/><linebreak/><b>Example</b> from Chief Justice Roberts: “<b>But</b> that argument . . . confuses mootness with the merits.”
Test Sentence:
In that case, however, this subtitle should tell you.
Corrected Test Sentence:
But this subtitle should tell you.

XML Rule:
<rule id="{new_rule_id}" name="BRIEFCATCH_FLOW_30136">
    <pattern>
        <token postag="SENT_START"/>
        <token>in</token>
        <token>that</token>
        <token>case</token>
        <token>,</token>
        <token regexp="yes">however|though</token>
        <token>,</token>
        <token regexp="yes">he|i|if|in|it|she|there|this</token>
    </pattern>
    <message>Could shortening your opening transition add punch and help lighten the style?|**Example** from Chief Justice Roberts: “**But** that argument . . . confuses mootness with the merits.”</message>
    <suggestion>But <match no="8"/></suggestion>
    <suggestion>Then<match no="7"/> <match no="8"/></suggestion>
    <suggestion>But then <match no="8"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":3,"priority":"8.252","WORD":true,"OUTLOOK":true}</short>
    <example correction="But this|Then, this|But then this"><marker>In that case, however, this</marker> subtitle should tell you.</example>
</rule>


###

Ad Hoc:
the aim of DT ( NN NN:U NN:UN !analysis !council !game !present !project !research !study !work ) is to VB
Rule Number:
30117
Correction:
$3 $4 seeks $6 $7
Category:
Conciseness
Explanation:
Would using fewer words help tighten the sentence?<linebreak/><linebreak/><b>Example</b> from Justice Stevens: “The holder class action that respondent <b>tried to plead</b> . . . is distinguishable from a typical Rule 10b–5 class action in only one respect[.]”<linebreak/><linebreak/><b>Example</b> from Eric Holder: “Now, more than a decade later, [Plaintiffs] <b>seek to hold</b> . . . .”<linebreak/><linebreak/><b>Example</b> from Deanne Maynard: “The industry <b>sought to</b> justify that time period by arguing that patents did not adequately protect investment in biologics[.]”
Test Sentence:
The aim of this book is to give general advice.
Corrected Test Sentence:
This book seeks to give general advice.

XML Rule:
<rule id="BRIEFCATCH_281025868524827903719537260966583393237" name="BRIEFCATCH_CONCISENESS_30117">
	<pattern>
		<token>the</token>
		<token>aim</token>
		<token>of</token>
		<token postag="DT"/>
		<token postag="NN|NN:U|NN:UN" postag_regexp="yes">
			<exception regexp="yes">analysis|council|game|present|project|research|study|work</exception>
		</token>
		<token>is</token>
		<token>to</token>
		<token postag="VB"/>
	</pattern>
	<message>Would using fewer words help tighten the sentence?|**Example** from Justice Stevens: “The holder class action that respondent **tried to plead** . . . is distinguishable from a typical Rule 10b-5 class action in only one respect[.]”|**Example** from Eric Holder: “Now, more than a decade later, [Plaintiffs] **seek to hold** . . . .”|**Example** from Deanne Maynard: “The industry **sought to** justify that time period by arguing that patents did not adequately protect investment in biologics[.]”</message>
	<suggestion><match no="4"/> <match no="5"/> seeks <match no="7"/> <match no="8"/></suggestion>
	<short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"8.328","WORD":true,"OUTLOOK":true}</short>
	<example correction="This book seeks to give"><marker>The aim of this book is to give</marker> general advice.</example>
</rule>

###

Ad Hoc:
( RX(.*?) !bed !conform !doctor !him !house !office !out !place !room !them !you ) as ( closely fast quickly simply soon ) as possible
Rule Number:
30118
Correction:
$0 $2
Category:
Conciseness
Explanation:
Would using fewer words help tighten the sentence?
Test Sentence:
Say it as simply as possible. 
Corrected Test Sentence:
Say it simply.

XML Rule:
<rule id="BRIEFCATCH_85326884043711870554689824506910775620" name="BRIEFCATCH_CONCISENESS_30118">
	<pattern>
		<token>
			<exception regexp="yes">bed|conform|doctor|him|house|office|out|place|room|them|you</exception>
		</token>
		<token>as</token>
		<token regexp="yes">closely|fast|quickly|simply|soon</token>
		<token>as</token>
		<token>possible</token>
	</pattern>
	<message>Would using fewer words help tighten the sentence?</message>
	<suggestion><match no="1"/> <match no="3"/></suggestion>
	<short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"5.262","WORD":true,"OUTLOOK":true}</short>
	<example correction="it simply">Say <marker>it as simply as possible</marker>.</example>
</rule>

###

Here are some abbreviations and their meanings that will be helpful in creating these rules:
I.             Part of Speech Tags 
CC Coordinating conjunction: for, and, nor, but, or, yet, so			
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
II.             Regular Expressions Used in Rules			
RX(.*?) A token that can be any word, punctuation mark, or symbol.			
RX([a-zA-Z]*) A token that can be any word.			
RX([a-zA-Z]+) A token that can be any word.			
III. Rules			
Rules consist of a number of tokens, some are required and some are optional.			
In the corrections, the first token is referred to as $0, the second $1, and so forth.			
If at least one word or tag or regular expression appears inside parentheses/brackets, the entire string, including the parentheses/brackets, is considered a single token.			
If at least two words or tags or regular expressions appear inside parentheses/brackets and if there is no “~” symbol at the end of the string, then any one of those words or tags or regular expressions is a required token in the string.			
If at least one word or tag or regular expression appears inside parentheses/brackets and if there is a “~” symbol at the end of the string, then any one of those words or tags or regular expressions is an optional token in the string.			
When a word or Part of Speech tag is preceded by “!”, that word or tag is excluded from the token. For example, "( CT(be) !been )" would include "be", "is", "am", "are", and "was", "were", and "being", but it would not include "been". Thus, the rule "( CT(be) !been ) happy" would flag "He was happy" but not "He had been happy".			
“SKIP” is always followed by a cardinal number. The number tells you how many tokens can come between the preceding token and the next one. The string “dog SKIP4 cat”, for example, would flag “The dog likes the cat” but would not flag “The dog likes the neighbor’s old cat,” nor would it flag “The cat likes the dog”.			
A backward slash “\” before a word means a special character or case-sensitive.			
“CT” refers to the infinitive form of a verb that can be conjugated. “CT(read)”, for example, could be “reads”, “read”, “reading”, etc.			
IV.          Corrections			
Corrections in the example tag provide the text that will replace everything inside the `marker` tags. Make sure when creating these, the corrected sentence would make sense when substituting in the correction. This would include no overlapping or duplicated words. However, and this is very important, if a word does not match the pattern for the rule, do not include it in the correction or within the marker tags.
Sometimes a rule has more than one possible correction. In that case, multiple alternative corrections are separated by the “@” symbol.			


Important Notes:
- Always set the rule id to `{new_rule_id}`
- Only return the rule XML, do not introduce it or wrap it with back ticks.
- If the ad hoc version has a part of speech tag in the same parentheses as suggestions, use the `<or>...</or>` tag with the part of speech tag as one token and the other options as a regexp token. for example with the input: 
keep the change ( NNPS how that when)
the output pattern would be:
<pattern>
  <token>keep</token>
  <token>the</token>
  <token>change</token>
  <or>
    <token postag="NNPS"/>
    <token regexp="yes">how|that|when</token>
  </or>
</pattern>
  - Note how the or tag is applied ONLY when the part of speech tag is inside the same parentheses as "how that when". Do not use the or tag if a part of speech tag is separate from other options. If using the or tag, make sure to use the regexp field and include multiple options in one token separated by `|`.
- The only instance that marker tags should be in the pattern is if there is a SENT_START postag in a token in the pattern. In this case, all tokens that succeed the SENT_START token need to be nested within marker tags, so that the SENT_START token is applied correctly.
- When converting the explanation to the message tag, make sure to convert any HTML notation to its markdown equivalent.
- The exception tags are only used for words that are marked with `!`. If you see you need to make an exception tag, make a note of this in your thoughts to determine which group of options needs to be exceptions and which are regular regexp.

Write your thoughts breaking down each part of the rule you are about to write, surround these thoughts in tags like <THOUGHT>...</THOUGHT>. Write up to 100 words thinking through your choices and considering the rules laid out
"""


NEW_CREATE_RULE_FROM_ADHOC_SYSTEM_PROMPT = """
You are a component in a system designed to take in a rule in "ad hoc" syntax and return it as a complete and valid XML. You will need to create the XML following the instructions provided below.

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

When creating a rule, set the `id` attribute to `id="{new_rule_id}"` every time.

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
Another example of or tokens:
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

Suggestion tags provide the text that will replace the matched pattern. The `<suggestion>` tags often utilize dynamic elements to construct their recommendations based on the specific content matched by the `<pattern>`. 

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

### <marker> placement in <example> tags

When placing the <marker> tag in the <example> tag for the pattern, the <marker>...</marker> tags need to surround ONLY (!) the text in the example sentence that MATCHES (!) the pattern. For example in the rule:
```
<pattern>
    <token>plain</token>
    <token>error</token>
    <token regexp="yes">analysis|doctrine|exception|inquiry|standard|test</token>
</pattern>
<suggestion>plain-error <match no="3"/></suggestion>    
<example correction="plain-error standard">The third prong of the Carines <marker>plain error standard</marker> is good law.</example>
```
The marker tags surround the substring "plain error standard" because those are the only words that match the <pattern> tokens. Therefore, the correction ONLY (!) contains the text that would replace the text within the <marker>...</marker> and is created based upon the <suggestion> tag.


## Additional Attributes

Correct use of attributes for the token and exception tags:
- The postag_regexp="yes" attribute should only be applied if there are multiple postags as regexp options, or if there is at least one open postag like V.*? or N.*?
- For the inflection attribute, if there are multiple regexp options or exceptions with an inflection attribute, there needs to be both an inflected="yes" AND a regexp="yes" attribute in the opening tag of that token/exception


## Message tag 

- The <message> tag will be provided as the Explanation field in the user input. When message is provided, it will have HTML tags. You will need to translate any HTML formatting into markdown. For example, if text is given with <i>...</i> tags like this `I <i>really love</i> xml.` This would become `I *really love* xml.`.
- Handle any HTML formatting like <i> and <b>
- <linebreak/> becomes `|`. If there are multiple linebreak tags next to each other like `<linebreak/><linebreak/>` this would just become one `|` symbol.


## Formatting:

### Order
The elements in the new rule need to be in the following order: 
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


# PART II: Interpreting Ad Hoc Inputs

The previous section provides instructions for how to make valid xml rules. This part will describe how you should create the rule using user instructions. When creating rules, it is critically important that the restrictions described above are respected. 

The user will provide you with an "Ad Hoc Syntax" representation of the pattern, the new "Rule Number", the "Correction" which will translate into the <suggestion> tags, the "Category" of the rule in the name, the "explanation" which will become the <message> tag, and finally the "Test Sentence" and "Test Sentence Correction" which will be used to create the <example> tag.

# Ad Hoc Syntax
This field is used to create the <pattern> in the new rule. Below are instructions on how to interpret the ad hoc syntax, make sure to pay particular attention to this because it is vital to get right:


## General Token Information
- Regular Words: If a single word is by itself and not in a (parenthesis), then this is an individual token. For example in the input `there are no` corresponds to the following tokens:
```
<token>there</token>
<token>are</token>
<token>no</token>
```
- If a set of words surrounded by parenthesis is given, then this token is a regular expression token that should contain all of the words within the parenthesis, with each separated by a "|" character. For example, the instructions `(very simple obvious) fact that` corresponds to the following tokens:
```
<token regexp="yes">very|simple|obvious</token>
<token>fact</token>
<token>that</token>
```
- Tokens can have part-of-speech tags. For example an ad hoc input like this `( NNP how that the what when )` corresponds to the following tokens:
```
<or>
    <token postag="NNP"/>
    <token regexp="yes">how|that|the|what|when</token>
</or>
```


### Operators: `!`,`~`,`/`

- an exclamation mark `!` indicates that token should be part of an exception 
- a tilde `~` indicates that the `min` attribute of that token needs to be added like so `min="0"` in the opening tag of that token tag in the output. That is, if the action provided by the user has a tilde (~) symbol, you must add to the corresponding token the attribute `min="0"`.
- a forward slash `/` indicates that the word should be case sensitive. By default case_sensitive="no", if the token needs to be case_sensitive="yes," this will be designated by putting a "/" character before the word whose token should have the case_sensitive="yes" attribute


### Open Token: `RX(.*?)`

- Open tokens are indicated by 'RX(.*?)' 
- Open tokens are coded as <token/> 
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

### Infelction: `CT()`

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

### case sensitive

Case Sensitive: Another token property is case_sensitive="yes". By default case_sensitive="no", if the token needs to be case_sensitive="yes," this will be requested by putting a "/" character before the word whose token should have the case_sensitive="yes" attribute. For example: 
Input:
"/They"
Output:
```
<token case_sensitive="yes">They</token>  
```

### Complex regexp tokens

Some of the ad hoc input you will be given is complex and you need to pay close attention to each piece to get it right. Here is an example of a complex ad hoc token:
```
( PRP:$ !his !her )
```
This has multiple pieces to consider:
- a POS tag "PRP:$" (possessive pronoun)
- two exceptions, "his" and "her"
This would translate into the following XML tokens:
```
<token postag="PRP:$">
    <exception regexp="yes">him|her</exception>
</token>
```
Note: in the output token that the multiple exceptions are included in one <exception> tag with the `regexp="yes"` attribute, but the <token> tag does not have the regexp attribute.


## Examples 

Below are a series, delimited by tripple equal signs (===), of examples of user inputs and expected outputs.

===

# Input:
Ad Hoc:
CT(be) ( fairly quite rather somewhat ) ( afraid available clear difficult easy essential good important likely necessary possible ready similar sure true wrong )
Rule Number:
30122
Correction:
$0 $2
Category:
Conciseness
Explanation:
Would cutting this implied modifier help strengthen the sentence?
Test Sentence:
It is quite easy to rewrite an article. 
Corrected Test Sentence:
It is easy to rewrite an article.

XML Rule:

# Output:
<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30122">
    <pattern>
            <token inflected="yes">be</token>
            <token regexp="yes">fairly|quite|rather|somewhat</token>
            <token regexp="yes">afraid|available|clear|difficult|easy|essential|good|important|likely|necessary|possible|ready|similar|sure|true|wrong</token>
    </pattern>
    <message>Would cutting this implied modifier help strengthen the sentence?</message>
    <suggestion><match no="1"/> <match no="3"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"3.249","WORD":true,"OUTLOOK":true}</short>
    <example correction="is easy">It <marker>is quite easy</marker> to rewrite an article.</example>
</rule>

===

# Input:
Ad Hoc:
(CT(be) and but they i he they have ) not ( generally typically usually ) ( RX(.*?) !accepted !considered !known )
Rule Number:
30124
Correction:
$0 rarely $3 @ $0 seldom $3 
Category:
Conciseness
Explanation:
Would using fewer words help tighten the sentence?
Test Sentence:
They are not generally definite articles.
Corrected Test Sentence:
They are rarely definite articles.

XML Rule:

# Output:
<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30124">                                        
    <pattern>                                
        <or>                        
            <token inflected="yes">be</token>                
            <token regexp="yes">and|but|they|i|he|they|have</token>                
        </or>                        
        <token>not</token>                        
        <token regexp="yes">generally|typically|usually</token>                        
        <token>                        
            <exception regexp="yes">accepted|considered|known</exception>                
        </token>                        
    </pattern>                                
    <message>Would using fewer words help tighten the sentence?</message>                                
    <suggestion><match no="1"/> rarely <match no="4"/></suggestion>                                
    <suggestion><match no="1"/> seldom <match no="4"/></suggestion>                                
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":2,"priority":"4.174","WORD":true,"OUTLOOK":true}</short>                                
    <example correction="are rarely definite|are seldom definite">They <marker>are not generally definite</marker> articles.</example>                                
</rule>

===

# Input:
Ad Hoc:
CT(do) not ( generally typically usually ) ( VB !give !include !take )
Rule Number:
30125
Correction:
rarely $3-$0 @ seldom $3-$0 
Category:
Conciseness
Explanation:
Would using fewer words help tighten the sentence?
Test Sentence:
They do not generally required a definite article.
Corrected Test Sentence:
They rarely require a definite article.

XML Rule:

# Output:
<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30125">
    <pattern>
        <marker>
            <token inflected="yes">do</token>
            <token>not</token>
            <token regexp="yes">generally|typically|usually</token>
            <token postag="VB" postag_regexp="yes">
                <exception regexp="yes">give|include|take</exception>
            </token>
        </marker>
    </pattern>
    <message>Would using fewer words help tighten the sentence?</message>
    <suggestion>rarely <match no="4"/></suggestion>
    <suggestion>seldom <match no="4"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":2,"priority":"5.262","WORD":true,"OUTLOOK":true}</short>
    <example correction="They rarely require|They seldom require">They <marker>do not generally require</marker> a definite article.</example>
</rule>

===

# Input:
Ad Hoc:
SENT_START in that case , ( however though ) , ( i he if in it she there this )
Rule Number:
30136
Correction:
But $7 @ Then $6 $7 @ But then $7
Category:
Flow
Explanation:
Could shortening your opening transition add punch and help lighten the style?<linebreak/><linebreak/><b>Example</b> from Chief Justice Roberts: “<b>But</b> that argument . . . confuses mootness with the merits.”
Test Sentence:
In that case, however, this subtitle should tell you.
Corrected Test Sentence:
But this subtitle should tell you.

XML Rule:

# Output:
<rule id="{new_rule_id}" name="BRIEFCATCH_FLOW_30136">
    <pattern>
        <token postag="SENT_START"/>
        <marker>
            <token>in</token>
            <token>that</token>
            <token>case</token>
            <token>,</token>
            <token regexp="yes">however|though</token>
            <token>,</token>
            <token regexp="yes">he|i|if|in|it|she|there|this</token>
        </marker>
    </pattern>
    <message>Could shortening your opening transition add punch and help lighten the style?|**Example** from Chief Justice Roberts: “**But** that argument . . . confuses mootness with the merits.”</message>
    <suggestion>But <match no="8"/></suggestion>
    <suggestion>Then<match no="7"/> <match no="8"/></suggestion>
    <suggestion>But then <match no="8"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":3,"priority":"8.252","WORD":true,"OUTLOOK":true}</short>
    <example correction="But this|Then, this|But then this"><marker>In that case, however, this</marker> subtitle should tell you.</example>
</rule>
"""


DYNAMIC_RULE_CHECKING_PROMPT = """
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
- How many <pattern> tags does this rule have?
- How many <example> tags corresponding to patterns (i.e. example tags with correction attribute and marker tags) does this rule have? This number should match the number of <pattern> tags.
- How many <antipattern> tags does this rule have?
- How many example tags corresponding to antipatterns (i.e. example tags that contain neither correction attributes nor marker tags) does this rule have? This number should match the number of <antipattern> tags.
- Do the <marker>...</marker> tags in the example tags span the section of text represented by the pattern?
- How many suggestion tags does this rule have?
- Are all suggestion tags represented in the correction field of the example tags?

How to respond: 
- If the rule xml meets all the criteria established in 'PART I XML Rules', you should respond back with the same string provided to you. 
- If the rule xml violates the criteria established in 'PART I XML Rules', you should respond back with the corrected version of the rule xml.

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
<thought>There is only one pattern, therefore there should only be one example tag. In the incorrect rule, an example tag had been created for each option substituting in the third token from the rule pattern. This is incorrect and since there is only one suggestion, we don't need to have multiple options in the correction attribute.</thought>
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
<thought>The marker tag in the example was excluding the word 'medicine' from the match. 'medicine' is one of the options for the second token in the pattern, therefore it should be included with the `<marker>...</marker>`</thought>
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
<thought>There is only one suggestion tag, therefore we do not need to have multiple options for the correction attribute for the example tag. The only time we would have multiple options for the example tag separated by `|` symbols would be if a rule had multiple suggestions. In the corrected rule we will use only one of the possibilities from the suggestion for the correction.</thought>
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
<thought>This rule was missing an example for the antipattern tag. To make it valid, there must be an example for each pattern and antipattern in a rule. These examples must contain a match for the pattern or antipattern they represent.</thought>
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
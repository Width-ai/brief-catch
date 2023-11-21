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

###

Note: how in the above examples in the rules, the markers surround the text being replaced. This is vital for the examples.

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
Example:			
the ( possibility probability likelihood ) to ( VB !can !case !contract !counsel !court !dissent !district !equal !even !evidence !found !jail !judge !motion !people !respect !source !still !title !trial !up !view !while !will ) ( and or ) ( to ~ ) ( VB !can !case !contract !counsel !court !dissent !district !equal !even !evidence !found !jail !judge !motion !people !respect !source !still !title !trial !up !view !while !will )			
This string would flag “the possibility to sing and dance”. It would flag “the likelihood to sing and dance”. It would flag “the likelihood to sing and to dance”. But it would not flag “the possibility to sing but dance”. It would not flag “the probability to respect or deny”.			
IV.          Corrections			
Corrections manipulate and transform any text flagged by a rule. The corrections refer to the rule tokens by number. $0 refers to the first token, $1 to the second, and so on.			
When a token number or word is preceded by a hyphen, what precedes the hyphen tells you what to do with that numbered token or word. If a rule is “CT(run) fast”, for example, and if the correction for that rule is “sprint-$0”, then the correction of the phrase “he ran fast” would be “he sprinted”, because “ran” is the past tense of “run” and “sprinted” is the past tense of “sprint.” If a rule is “CT(succeed) in VBG”, for example, and if the correction for that rule is “$2-$0”, then the correction for the phrase “she succeeded in reaching the top” would be “she reached the top”.			
Sometimes a rule has more than one possible correction. In that case, multiple alternative corrections are separated by the “@” symbol.			


Important Notes:
- always set the rule id to `{new_rule_id}`
- do not surround your response with "```xml...```"
"""
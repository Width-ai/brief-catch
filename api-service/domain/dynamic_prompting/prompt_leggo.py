VALIDATE_RULE_PROMPT = """
You are a system focused on making sure the XML rule <pattern> is a match with the <example> and <suggestion> for the same exact rule based on our mapping. Here's some examples of matches:

{example_rules}   

Here are what the abbreviations mean when making modifications to the rules. 

I. Part of Speech Tags:
{part_of_speech} 

{regex_rules} 

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

IV. Corrections
Corrections in the example tag provide the text that will replace everything inside the `marker` tags. Make sure when creating these, the corrected sentence would make sense when substituting in the correction. This would include no overlapping or duplicated words. However, and this is very important, if a word does not match the pattern for the rule, do not include it in the correction or within the marker tags.
Sometimes a rule has more than one possible correction. In that case, multiple alternative corrections are separated by the “@” symbol.
"""

GENERAL_INSTRUCTIONS_PROMPT = """
Here are what the abbreviations mean when making modifications to the rules. 

I. Part of Speech Tags:
{part_of_speech} 

{regex_rules} 

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

IV. Corrections
Corrections in the example tag provide the text that will replace everything inside the `marker` tags. Make sure when creating these, the corrected sentence would make sense when substituting in the correction. This would include no overlapping or duplicated words. However, and this is very important, if a word does not match the pattern for the rule, do not include it in the correction or within the marker tags.
Sometimes a rule has more than one possible correction. In that case, multiple alternative corrections are separated by the “@” symbol.
"""

REGEX_INSTRUCTIONS_PROMPT = """
II. Regular Expressions Used in Rules
RX(.*?) A token that can be any word, punctuation mark, or symbol.
RX([a-zA-Z]*) A token that can be any word.
RX([a-zA-Z]+) A token that can be any word.
"""

SPLITTING_FEWSHOT_PROMPT = """
For example, below are three rules ("PUNCHINESS_377","PUNCHINESS_377.1","PUNCHINESS_377.2") delimited by tripple back quotes. 


```
<rule id="BRIEFCATCH_147725296952682099987839530434290533040" name="PUNCHINESS_377">
    <antipattern>
        <token regexp="yes">can|could|shall|should</token>
        <token>ascertain</token>
    </antipattern>
    <antipattern>
        <token inflected="yes">ascertain<exception>ascertaining</exception></token>
        <token min="0" skip="5"/>
        <token regexp="yes">intent|meaning|standing|truth</token>
    </antipattern>
    <antipattern>
        <token inflected="yes">ascertain<exception>ascertaining</exception></token>
        <token>the</token>
        <token>citizenship</token>
    </antipattern>
    <antipattern>
        <token inflected="yes">ascertain<exception>ascertaining</exception></token>
        <token>their</token>
    </antipattern>
    <antipattern>
        <token>ascertain</token>
        <token>whether</token>
    </antipattern>
    <pattern>
        <token inflected="yes">ascertain<exception>ascertaining</exception></token>
    </pattern>
    <message>Would direct language convey your point just as effectively?|**Example** from Chief Justice Roberts: "The SEC . . . is not like an individual victim who relies on apparent injury to **learn of** a wrong."|**Example** from Judge Nalbandian: "The same day that her son lodged his complaints . . . , police . . . told her to come to the police station to **find out about** her son."|**Example** from Juanita Brooks: "In *Keystone*, after obtaining a patent, the patentee **learned of** a possible prior use of its invention."|**Example** from Jeff Lamken: "If the President **determined** that the SEC Commissioners were neglecting their duty to regulate the securities markets, he could remove the Commissioners[.]"|**Example** from YouTube’s terms of service: "Among other things, you can **find out about** YouTube Kids, the YouTube Partner Program . . . ."</message>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">determine</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">learn</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">establish</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">discover</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">find</match> out</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">figure</match> out</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">decide</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">arrive</match> at</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">learn</match> of</suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":9,"priority":"1.53","WORD":true,"OUTLOOK":true}</short>
    <example correction="determined|learned|learnt|established|discovered|found out|figured out|decided|arrived at|learned of|learnt of">She <marker>ascertained</marker> the item's whereabouts.</example>
    <example>We can ascertain their intent from the examples provided</example>
    <example>Ascertain its intent.</example>
    <example>To ascertain the citizenship.</example>
    <example>We couldn't ascertain their intent.</example>
    <example>It is crucial to ascertain whether the facts are true.</example>
</rule>
```

```
<rule id="BRIEFCATCH_147725296952682099987839530434290533040" name="PUNCHINESS_377.1">
    <antipattern>
        <token regexp="yes">can|could|shall|should</token>
        <token>ascertain</token>
    </antipattern>
    <antipattern>
        <token inflected="yes">ascertain<exception>ascertaining</exception></token>
        <token min="0" skip="5"/>
        <token regexp="yes">intent|meaning|standing|truth</token>
    </antipattern>
    <antipattern>
        <token inflected="yes">ascertain<exception>ascertaining</exception></token>
        <token>the</token>
        <token>citizenship</token>
    </antipattern>
    <antipattern>
        <token inflected="yes">ascertain<exception>ascertaining</exception></token>
        <token>their</token>
    </antipattern>
    <antipattern>
        <token>ascertain</token>
        <token>whether</token>
    </antipattern>
    <pattern>
        <token inflected="yes">ascertain<exception>ascertaining</exception></token>
    </pattern>
    <message>Would direct language convey your point just as effectively?|**Example** from Chief Justice Roberts: "The SEC . . . is not like an individual victim who relies on apparent injury to **learn of** a wrong."|**Example** from Judge Nalbandian: "The same day that her son lodged his complaints . . . , police . . . told her to come to the police station to **find out about** her son."|**Example** from Juanita Brooks: "In *Keystone*, after obtaining a patent, the patentee **learned of** a possible prior use of its invention."|**Example** from Jeff Lamken: "If the President **determined** that the SEC Commissioners were neglecting their duty to regulate the securities markets, he could remove the Commissioners[.]"|**Example** from YouTube’s terms of service: "Among other things, you can **find out about** YouTube Kids, the YouTube Partner Program . . . ."</message>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">determine</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">learn</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">establish</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">discover</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">find</match> out</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">figure</match> out</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">decide</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">arrive</match> at</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">learn</match> of</suggestion>
    <short>{"ruleGroup":BRIEFCATCH_PUNCHINESS_377,"ruleGroupIdx":1,"isConsistency":false,"isStyle":true,"correctionCount":9,"priority":"1.53","WORD":true,"OUTLOOK":true}</short>
    <example correction="determined|learned|learnt|established|discovered|found out|figured out|decided|arrived at|learned of|learnt of">She <marker>ascertained</marker> the item's whereabouts.</example>
    <example>We can ascertain their intent from the examples provided</example>
    <example>Ascertain its intent.</example>
    <example>To ascertain the citizenship.</example>
    <example>We couldn't ascertain their intent.</example>
    <example>It is crucial to ascertain whether the facts are true.</example>
</rule>
```

```
<rule id="BRIEFCATCH_147725296952682099987839530434290533041" name="PUNCHINESS_377.2">
    <pattern>
        <token inflected="yes">ascertain</token>
        <token>whether</token>
    </pattern>
    <message>Would direct language convey your point just as effectively?</message>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">determine</match> /2</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">decide</match> /2</suggestion>
    <short>{"ruleGroup":BRIEFCATCH_PUNCHINESS_377,"ruleGroupIdx":2,"isConsistency":false,"isStyle":true,"correctionCount":2,"priority":"1.53","WORD":true,"OUTLOOK":true}</short>
    <example correction="determine whether|decide whether">They will <marker>ascertain whether</marker> a construction of the statute is fairly possible.</example>
</rule>
```
Observe that "PUNCHINESS_377.1" and "PUNCHINESS_377.2" are derived by splitting the "PUNCHINESS_377" into two separate components

Explanation:
The original rule has an antipattern for the sequence "ascertain whether"
Upon reviewing the ngram data for that sequence vs. the rule`s suggestions applied to
that sequence (which if not for the antipattern would be triggered) -
so "ascertain whether" vs. "decide whether", "determine whether", etc. - 
the results indicated that at least some of the suggestions - 
in particular the "determine whether" and "decide whether" - 
score higher in ngram than the original "ascertain whether".
And that in turn results in a "rule split" in a sense that we need to 
create an additional rule just for the sequence "ascertain whether" with 
only the 2 suggestions "decide" and "determine".


Do not modify the **ID** or the **name** of the output rules.
"""

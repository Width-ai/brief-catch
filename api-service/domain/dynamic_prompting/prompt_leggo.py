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

REGEX_INSTRUCTIONS_PROMPT = """
II. Regular Expressions Used in Rules
RX(.*?) A token that can be any word, punctuation mark, or symbol.
RX([a-zA-Z]*) A token that can be any word.
RX([a-zA-Z]+) A token that can be any word.
"""

import re
from typing import Dict, List
from utils.dynamic_prompting import get_pos_tag_dicts_from_rule
from domain.dynamic_prompting.parts_of_speech import POS_MAPS


ANTIPATTERN_INSTRUCTIONS = """
(1) Antipatterns begin and end with their tags on separate lines and only contains tokens that also have their respective tags:
<antipattern>
<token>...</token>
...
</antipattern>

(2) All antipatterns need to be located below the ‘<rule>’ opening tag and above the ‘<pattern>’ opening tag within the xml rule. In case the xml rule provided already contains one or more antipattern(s), count top down and insert the new antipattern into the rule at the specified position.
"""

CT_TAG_INSTRUCTIONS = """
Inflection exceptions: An inflected token with one or more words will be indicated by preceding it with "CT" and surrounding the word or words in parenthesis: CT(walk run !ran). This means you would create a token with the property "inflected="yes"" for the words walk|run, and then you would add a single exception for the word "ran." The exception would be inside the token like this:  
<token inflected="yes">walk|run<exception>ran</exception></token>  
"""


SUGGESTION_AND_EXAMPLE_INSTRUCTIONS = """
# suggestion and example tags
    
    Suggestion tags indicate how the text will be modified. Example tags show how the suggestion is applied to the text. Suggestion tags associated with a pattern have a `correction` attribute. The correction attribute says what the pattern will be corrected to. 

    For example, inspect the following suggestion and example tags. Notice how the text inside the example tags "good faith" matches the <pattern> tags and gets corrected to the <suggestion> tag in the example tag correction attribute:
    ```
    <pattern>
        <token>good</token>
        <token>faith</token>
    </pattern>
    <suggestion>good-faith</suggestion>
    <example correction="good-faith">good faith</example>
    ```

    In the <suggestion> tags, sometimes you will see a `match` tags. These match tags have a numeric `no` attribute. The `no` attribute indicates what token (in the pattern) must be inserted in that location in the corresponding example. For example, notice how <match no="2"> causes the example tag to slot in the second word "used" in the corrected example. 
    ```
    <pattern>
        <token>presently</token>
        <token>used</token>
    </pattern>
    <suggestion>now <match no="2"/></suggestion>
    <example correction="now used">The property is <marker>presently used</marker> for a different purpose.</example>
    ```

    Finally, when there is more than one suggestion tag, the correction in the example needs to take that into account by having a logical or operator "|". For example, notice how the two suggestion tags below translate to a correction attribute in the example tag with a:
    ```
    <suggestion><match no="1"/> on</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">ask</match></suggestion>
    <example correction="called on|asked">She was <marker>called upon</marker> three times.</example>
    ```
"""

SENT_START_INSTRUCTIONS = """
(7) Sent_Start Coding: Sent_Start is a POSTAG that counts as its own token at the start of the sentence. This means if Input 1 requests "SENT_START Hello" Then token 1 is <token postag="SENT_START"/>, token 2 is <token>hello</token>. When Sent_Start is used, the rest of the pattern must be offset from this token using <marker> </marker>.
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


def format_optimized_standard_prompt(
    replace_antipattern,
    target_element,
    replace_pos_tags,
    replace_pos_tags_fewshot_examples,
    replace_ct_tag,
    replace_backslash_number,
    replace_sent_start,
    replace_suggestion_and_example,
):
    return (
        f"""You will be given a rule, an element type to modify, and an action to take with specificities around the action in the user text. Modify the xml rule according to the info provided in sections 1 and 2.
    # Section 1:

    {replace_antipattern}

    (3) For <tokens> nested within the {target_element} please follow the below instructions to properly write the token lines of the {target_element}.  
    - For Regular Words: If a single word is by itself and not in a (parenthesis), then this is an individual token.
    - If a set of words surrounded by parenthesis is given, then this token is a regular expression token that will need to account for all of the words within the parenthesis, with each separated by a "|" character.
    - Punctuation is its own token.
    - Possessives are chunked as tokens splitting at the punctuation mark. So in Ross's, "Ross" is one token, "'s" is the second token. In Business', "Business" is one token, "'" is the second token.
    - An open token, which is indicated with ‘RX(.*?)’ is coded as <token/>. If you are told to generate a token for a pattern like `( RX(.*? ) !apples !bananas !grapes )`, that would translate to:
        <token><exception regexp="yes">apples|banans|grapes</exception></token>

    For example, with the input: "There (is was) a fight."  
    The output would be: 
    <antipattern>  
    <token>there</token>  
    <token regexp="yes">is|was</token>  
    <token>a</token>  
    <token>fight</token>  
    <token>.</token>  
    </antipattern>

    (4) Part-of-Speech Tags: These tokens take one of two forms: <token postag="POSTAG"/> or <token postag_regexp="yes" postag="CC|CD"/>. The postag_regexp="yes" line is required when either (i) there are more than one postag sought to be matched by the token; or (ii) when you use a broad part-of-speech tag that can capture several types of postags. An example would be V.*. This means any POSTAG that begins with V. So this would match a word that is tagged as VB, VBD, VBG, VBN, VBP, and VBZ. If you used N.*, this would match any word tagged as NN, NNS, NN:U, NN:UN, NNP, and NNPS. Here is the total list of part-of-speech tags currently recognized that you can use (the capital letters at the beginning are the actual tags you should use instead of "POSTAG" in the example above):  
    {replace_pos_tags}
    `` = Left open double quote
    , = Comma
    '' = Right close double quote
    . = Sentence-final punctuation (in LanguageTool, use SENT_END instead)
    : = Colon, semi-colon
    $ = Dollar sign
    # = Pound sign


    Here are some examples for creating tokens with Part-of-Speech tags:

    {replace_pos_tags_fewshot_examples}

    (5) Exception tags:
    Exceptions come between the <token> and </token> lines of code. They are used to exclude words that would be matched otherwise by the part-of-speech tag in a token. When creating exception tags, pay attention to these rules:
    - If there is a single word to be added as an exception, then it can be added like this: <exception>dog</exception> (excepts the word dog).
    - If there are several, then like a token you MUST include the regexp="yes" attribute and separate the words with the "|" character: <exception regexp="yes">cat|dog</exception> (excepts the words cat and dog from the token).

    Here are some examples on creating exceptions:

    Example Input: (VB !swim !run !walk) 
    (Thoughts: Here the token should match "VB" but the words "swim" "run" and "walk" should be excepted.) 
    Example Output:   
    <antipattern>  
    <token postag="VB">  
    <exception regexp="yes">swim|run|walk</exception>  
    </token>  
    </antipattern>  


    Complex exceptions: Sometimes the exceptions will need to include both Part of Speech tags (postags) and enumerated words. In this case, the two must be in separate exception lines.

    Example Input: V.* (!VBD !swim !run !walk)
    (Comment: Here the token should match "VB" but the words "swim" "run" and "walk" should be excepted)  
    Expected Output:   
    <antipattern>  
    <token postag_regexp="yes" postag="V.*">  
    <exception postag="VBD"/>  
    <exception regexp="yes">swim|run</exception>  
    </token>  
    </antipattern>  

    {replace_ct_tag}

    (6) Case Sensitive: Another token property is case_sensitive="yes". By default case_sensitive="no", if the token needs to be case_sensitive="yes," this will be requested by putting a "/" character before the word whose token should have the case_sensitive="yes" attribute. For example: 
    Example Input:
    /They
    Example Output:
    <token case_sensitive="yes">They</token>  

    {replace_sent_start}

    (8) Any time an antipattern is added or a pattern is modified, an example needs to be added to match the exact string of tokens of the new antipattern(s) or pattern. Please generate an exemplary phrase which matches the newly added antipattern or modified pattern and insert it into the rule as the last example:  
    In case the rule already contains antipatterns and examples for those antipatterns, add a new example for the newly added antipattern and insert it below after all other existing examples above the closing </rule> tag.

    {replace_suggestion_and_example}

    """
        + """

    # Section 2:
    (1) Remove all ‘,’ symbols following the ‘BRIEFCATCH_{number}’, the ‘BRIEFCATCH_{CATEGORYNAME}_{number}’, the ‘</pattern>’, each ‘</suggestion>, ‘</message>’, and ‘</example>’ object in the code provided in the input. Do not delete any other ‘,’ symbols in the code other than the ones specifically listed in the before sentence. Delete all spaces preceding or succeeding any "<" and ">" symbols in the code.

    (2) Insert a rule opening tag at the top of the new rule following this example:
    Example Input: BRIEFCATCH_311798533127983971246215325355996953264, BRIEFCATCH_PUNCHINESS_847.2,  
    Expected Output: <rule id="BRIEFCATCH_311798533127983971246215325355996953264" name="BRIEFCATCH_ PUNCHINESS_847.2 >

    (3) This short template will be added right below the last of the ‘</suggestion>’ tags in the rule and above the first ‘<example>’ tag in the rule. The only thing that should change is the number for the "correctionCount" value. This number will be the number of "<suggestion>" tags in the rule. Make sure to update only this value in the "<short>" tag in the final modified rule."""
        + """
    Here is a template for how the short tag should look:
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":true,"isStyle":true,"correctionCount":1,"priority":"9.7845","WORD":true,"OUTLOOK":true}</short>
    The only field you should be changing (if necessary) is the correctionCount.
    """
        + f""""
    (4) The elements in the modified rule need to be in the following order: 
    1. <rule(…)> (rule opening tag)
    2. <antipattern>(tokens)</antipattern> (all antipatterns one after another)
    3. <pattern>tokens</pattern> (pattern)
    4. <message>(...)</message> (message)
    5. <suggestion>(...)</suggestion> (all suggestions one after another)
    6. <short>(...)</short> (short)
    7. <example correction=”(...)”>(...)</example> (example for the pattern)
    8. <example>(...)</example> (all examples for antipatterns one after another)
    9. </rule> (closing rule tag)

    (5) Correct use of attributes for the token and exception tags:
    - The postag_regexp="yes" attribute should only be applied if there are multiple postags as regexp options, or if there is at least one open postag like V.*? or N.*?
    - For the inflection attribute, if there are multiple regexp options or exceptions with an inflection attribute, there needs to be both an inflected="yes" AND a regexp="yes" attribute in the opening tag of that token/exception
    - When there is a ~ symbol at the end of an adhoc token, the `min` attribute needs to be added like so `min="0"` in the opening tag of that tag in the output. That is, if the action provided by the user has a tilde (~) symbol, you must add to the corresponding token the attribute `min="0"`.

    (6) Consider the requests made in the "Specific Modifications" section. Are you being asked to change the order of tokens? Do you need to modify what already exists? Consider what changes are necessary to make to the existing rule and do them. Don't output your thoughts, just take action.
        (7.1) If asked to change a token, you may need to replace the original token specified in order for the change to be correct. The original element you are replacing should not effect how you generate a new one.

    (7) When creating tokens and exceptions for several words, make sure the words are in alphabetical order in the new tag.

    (8) Do NOT remove any of the `**` or `|` symbols from the content within the <message> tag. This is crucial, these symbols MUST remain in the <message> tag as given to you.
        (8.1) Do NOT modify the <message> tag at all from the original rule unless DIRECTLY specified to. Maintain its original form in all other cases.

    {replace_backslash_number}
    """
    )


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


def has_backslash_number(s):
    return "\<number>" in s


def has_sent_start(s):
    return "sent_start" in s.lower()


# main


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
    _replace_ct_tag = CT_TAG_INSTRUCTIONS if has_ct(specific_actions) else ""

    _replace_backslash_number = SUGGESTION_AND_EXAMPLE_INSTRUCTIONS

    SUGGESTION_AND_EXAMPLE_INSTRUCTIONS
    _replace_sent_start = (
        SENT_START_INSTRUCTIONS
        if has_sent_start(specific_actions + original_rule)
        else ""
    )
    return format_optimized_standard_prompt(
        replace_antipattern=_replace_antipattern,
        target_element=target_element,
        replace_pos_tags=_replace_pos_tags,
        replace_pos_tags_fewshot_examples=_replace_pos_tags_fewshot_examples,
        replace_ct_tag=_replace_ct_tag,
        replace_sent_start=_replace_sent_start,
        replace_suggestion_and_example=_replace_backslash_number,
    )

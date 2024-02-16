import json
import re
from typing import Dict, List, Tuple
from utils.logger import setup_logger
from utils.utils import call_gpt_with_backoff, generate_simple_message

logger = setup_logger(__name__)

SYSTEM_PROMPT = """# Task
You are a system focused on making sure the XML rule <pattern> and <antipattern> tags match with the <example> tags. 

# Pattern -> Example rules
(1)The <example> tags that correspond to the <pattern> incorporate the suggestion as a `correction` field and surround the part of the sentence that matches the pattern with <marker>...</marker> tags.
  (1.a) The <marker> tags **must** surround the full pattern of rule
(2) There **must** be an example for the pattern

# Antipattern -> Example rules
(1) The <example> tags that correspond to the <antipattern> do not contain `correction` fields or <marker>...</marker> tags, they just have an example sentence that includes a match for the <antipattern>
(2) A valid rule has only ONE <example> *per* <antipattern>. If a rule has three antipatterns, it needs three examples to be valid. The 1:1 ratio is crucial.


Here are some examples of how <pattern> and <antipattern> tags match <example> tags:


# Pattern Matching Examples
Pattern:
<pattern>
    <token inflected="yes">ascertain<exception>ascertaining</exception></token>
</pattern>
<suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">determine</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">learn</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">establish</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">discover</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">find</match> out</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">figure</match> out</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">decide</match></suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">arrive</match> at</suggestion>
    <suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">learn</match> of</suggestion>

Matching example:
<example correction="determined|learned|learnt|established|discovered|found out|figured out|decided|arrived at|learned of|learnt of">She <marker>ascertained</marker> the item's whereabouts.</example>


# Antipattern Matching Examples
--------
Antipattern:
<antipattern>
    <token regexp="yes">can|could|shall|should</token>
    <token>ascertain</token>
</antipattern>

Matching example:
<example>We can ascertain their intent from the examples provided</example>
--------
Antipattern:
<antipattern>
    <token inflected="yes">ascertain<exception>ascertaining</exception></token>
    <token>the</token>
    <token>citizenship</token>
</antipattern>

Matching example:
<example>To ascertain the citizenship.</example>
--------


Given the input rule, use the above instructions to validate the example tags. Specifically:
(a) if an example tag is correct, DO NOT CHANGE IT;
(b) write any examples that are missing;
(c) rewrite examples that need to be corrected.

Before making a decision, you should think through what example tags will be needed to be
(a) kept
(b) added
(c) rewritten to ensure this is a valid rule.

You should respond in the following JSON format with the following fields:
1. `thought`: a string field where you show your thought process around which rules should be kept, added or rewritten;
2. `examples`: an array field where each item is an example tag. Make sure that the `examples` array contains all example tags, whether they were kept unchanged, added or modified. 
"""


def validate_examples(xml: str, max_retry: int = 5) -> Tuple[str, List[Dict]]:
    examples = None
    retries = 0
    usages = []

    while examples is None and retries < max_retry:
        retries += 1
        message = generate_simple_message(SYSTEM_PROMPT, xml)
        resp, usage = call_gpt_with_backoff(
            message,
            response_format="json_object",
            model="gpt-4-0125-preview",
            temperature=0,
            max_length=1000,
        )
        usages.append(usage)
        logger.info(f"{resp=}")

        try:
            examples = json.loads(resp)["examples"]
        except json.JSONDecodeError:
            # Specifically catch JSON errors
            logger.error("bad json, retrying...")

    if examples:
        xml = re.sub(r"\n    <example.*?>.*?</example>", "", xml)
        example_section = "\n" + "\n".join(["    " + s for s in examples])
        end_of_xml_ix = -(len("<rule/>") + 2)
        xml_out = xml[:end_of_xml_ix] + example_section + xml[end_of_xml_ix:]
        return xml_out, usages
    return xml, usages

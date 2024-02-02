from typing import List
import re

import json
from utils.dynamic_prompting import get_pos_tag_dicts_from_rule, POS_MAPS
from utils.utils import generate_simple_message, call_gpt
from domain.dynamic_prompting.prompt_leggo import (
    GENERAL_INSTRUCTIONS_PROMPT,
    SPLITTING_FEWSHOT_PROMPT,
    REGEX_INSTRUCTIONS_PROMPT,
)


## split on or
def extract_or_tag(rule_xml: str) -> str:
    or_contentL = re.search(r"(<or>.*?</or>)", rule_xml, re.DOTALL)
    if not or_contentL:
        return None
    return or_contentL.group(1)


def extract_operands(or_input_string: str) -> List[str]:
    # regular expression to find <token> tags
    token_pattern = r"(<token.*?/>|<token.*?</token>)"
    # extract all <token> tags
    return re.findall(token_pattern, or_input_string, re.DOTALL)


def split_rule_by_or_operands(input_rule: str) -> List[str]:
    """
    TODO: currently does not handle case where rule has two or tags.

    """
    or_content = extract_or_tag(input_rule)
    if not or_content:
        return input_rule
    operand_list = extract_operands(or_content)

    split_rule = input_rule.split(or_content)
    operand_rules = []
    for operand_str in operand_list:
        operand_rule = f"{split_rule[0]}{operand_str}{split_rule[1]}"
        operand_rules.append(operand_rule)
    return operand_rules


## split rule that is too broad


def split_broad_rule_with_instructions(input_rule, user_considerations) -> List[str]:
    # grab part of speech tag from rule
    pos_tags_input_rule = get_pos_tag_dicts_from_rule(input_rule, list(POS_MAPS.keys()))
    # NOTE: prompt has the following POStags, including them manually here
    pos_tags_in_prompt = {
        "VB": "VB Verb, base form: eat, jump, believe, be, have",
        "VBD": "VBD Verb, past tense: ate, jumped, believed",
        "VBG": "VBG Verb, gerund/present participle: eating, jumping, believing",
        "VBN": "VBN Verb, past participle: eaten, jumped, believed",
        "VBP": "VBP Verb, non-3rd ps. sing. present: eat, jump, believe, am (as in 'I am'), are",
        "VBZ": "VBZ Verb, 3rd ps. sing. present: eats, jumps, believes, is, has",
    }
    all_pos = {**pos_tags_input_rule, **pos_tags_in_prompt}
    _replace_pos = "\n".join([f"{v}" for k, v in all_pos.items()])
    print(_replace_pos)
    from utils.dynamic_prompting import rule_has_regex

    if rule_has_regex(input_rule):
        _replace_regex = REGEX_INSTRUCTIONS_PROMPT
    else:
        _replace_regex = ""
    _replace_general_instruction = GENERAL_INSTRUCTIONS_PROMPT.format(
        part_of_speech=_replace_pos,
        regex_rules=_replace_regex,
    )
    _replace_task_instruction = """
    You are a language system used for modifying gramatical logic encoded as XML rules. 
    The user will provide you with (i) a rule that is deemed too broad (ii) some additional considerations. 
    Your task is to split (i) the rule that is too broad while taking into account (ii) the provided additional considerations. 
    Below I will provide you with some additional context and at the bottom of this message is an example of a rule being split.
    """

    final_prompt_template = """
    {task_instruction}

    {general_instructions}

    {splitting_fewshot}
    """

    system_prompt = final_prompt_template.format(
        task_instruction=_replace_task_instruction,
        general_instructions=_replace_general_instruction,
        splitting_fewshot=SPLITTING_FEWSHOT_PROMPT,
    )
    user_prompt = json.dumps(
        {
            "rule_deemed_too_broad": input_rule,
            "additional_considerations": user_considerations,
        },
    )
    model_response = call_gpt(
        messages=generate_simple_message(system_prompt, user_prompt),
        model="gpt-4-1106-preview",
    )
    return "TODO: parse model response for two rule xmls", model_response

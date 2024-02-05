from typing import List
import re
import json
from utils.dynamic_prompting import (
    get_pos_tag_dicts_from_rule,
    rule_has_regex,
    POS_MAPS,
)
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
    # NOTE: `SPLITTING_FEWSHOT_PROMPT` used in this prompt has the following POStags,
    # including them manually here:
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

    _replace_output_instructions = """Respond, in JSON format. Your output should contain two fields (`rule_1` and `rule_2`) with the split rules"""

    final_prompt_template = """
    {task_instruction}

    {general_instructions}

    {splitting_fewshot}

    {output_instructions}
    """

    system_prompt = final_prompt_template.format(
        task_instruction=_replace_task_instruction,
        general_instructions=_replace_general_instruction,
        splitting_fewshot=SPLITTING_FEWSHOT_PROMPT,
        output_instructions=_replace_output_instructions,
    )
    user_prompt = json.dumps(
        {
            "rule_deemed_too_broad": input_rule,
            "additional_considerations": user_considerations,
        },
    )
    model_response, usage = call_gpt(
        messages=generate_simple_message(system_prompt, user_prompt),
        model="gpt-4-0125-preview",
        max_length=4096,
        response_format="json_object",
    )
    # expect gpt response has a json with {'rule_1':str, 'rule_2':str}
    split_rules_dict = json.loads(model_response[0])
    rule_1 = split_rules_dict.get("rule_1", None)
    rule_2 = split_rules_dict.get("rule_2", None)
    new_rules = [rule_1, rule_2]
    return new_rules, usage

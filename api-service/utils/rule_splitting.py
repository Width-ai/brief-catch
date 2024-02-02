from typing import List
import re


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

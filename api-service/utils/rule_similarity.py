from typing import List, Dict
import re
from fuzzywuzzy import process
from domain.dynamic_modifier.template_rules import TEMPLATE_RULES


## logic for parsing down our rules
def encode_rule_as_pattern_string(xml_rule: str) -> str:
    """
    This function takes in a rule xml.
    Checks for the existence of patterns in the rule.
    Returns matches joined by `|`
    """
    patterns = [
        r'<match no="\d+"/>',
        r'regexp="[^"]*"',
        r'postag="([^"]*)"',
        r'postag_replace="([^"]*)"',
        r"<example[^>]*>.*?</example>",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, xml_rule)
        if matches:
            return "|".join(matches)

    return ""


# TODO: confirm return type
def calculate_similarity_between_rules(
    rule_xml_1: str,
    rule_xml_2: str,
) -> tuple[str, float]:
    """
    note process.extract is actually meant to handle a list in its second argument. we could in principle have just passed process.extract(rule_xml_1,list_of_exemplar_rules) but I chose this implementation for readability since the performance difference is negligible.
    """
    tags_rule_1 = encode_rule_as_pattern_string(rule_xml_1)
    tags_rule_2 = encode_rule_as_pattern_string(rule_xml_2)
    return process.extract(tags_rule_1, [tags_rule_2], limit=None)[0]


def get_similar_template_rules(
    input_rule_xml: str,
    template_rules: Dict[int, str] = TEMPLATE_RULES,
) -> List:
    """
    replaces `return_best_examples_on_logic`
    rerturns a list of template rules sorted by similarity score
    """
    # [(rule_id, (rule_xml, similarity_score)), ..]
    sim_rule_to_templates = [
        (rule_id, calculate_similarity_between_rules(input_rule_xml, r))
        for rule_id, r in template_rules.items()
    ]

    # sort by similairty score, highest first
    sorted_sim_rule_to_templates = sorted(
        sim_rule_to_templates,
        key=lambda x: x[1][1],
        reverse=True,
    )

    return [
        template_rules[id_and_rule[0]] for id_and_rule in sorted_sim_rule_to_templates
    ]

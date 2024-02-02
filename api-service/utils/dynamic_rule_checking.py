import re
from typing import List, Dict
from fuzzywuzzy import process


from domain.dynamic_modifier.parts_of_speech import POS_MAPS
from domain.dynamic_modifier.prompt_template import PROMPT_TEMPLATE
from domain.dynamic_modifier.template_rules import TEMPLATE_RULES
from utils.utils import call_gpt_with_backoff, generate_simple_message

# import openai
# from dotenv import load_dotenv
# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")


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


def get_pos_tag_dicts_from_rule(
    rule_xml: str,
    all_pos: list[str],
) -> dict[str, str]:
    """
    takes in a rule xml and a list of available pos_map dicts
    returns a list of pos_tag_dict
    """
    # find tokens that have a postag
    # rule_xml = TEMPLATE_RULES[1]
    matches = re.findall(r'<token postag=".*?>', rule_xml)

    # extract the contents of the postag
    pos_tags = [m.split('"')[1] for m in matches]

    # find pos_tags that start with the base form
    matching_tags = {}
    for pos_tag in pos_tags:
        # extract the base form of the pos tag
        if ".*" in pos_tag:
            base_form = pos_tag.replace(".*", "")
        else:
            base_form = pos_tag
        # find pos_tags that start with the base form
        for pos_key in all_pos:
            if pos_key.startswith(base_form):
                matching_tags[pos_key] = POS_MAPS[pos_key]

    return matching_tags


def check_rule_modification(input_rule_xml: str) -> str:
    """
    1. 3 example known valid rules that are most similar to rule
    2. POS tags that are present in input rule
    3. if regex appears in input rule, include regex rules
    4. additional cleaning
    5. call model and check response. maybe call again for correction
    """
    usages = []
    # 1. find xml rules that are similar to input rule
    matching_examples = get_similar_template_rules(input_rule_xml)

    # matching_examples = [
    #     xml_string.replace("</pattern>", "</pattern>\n        Suggestion & Example:")
    #     for xml_string in matching_examples
    # ]

    # 2. grab pos tags present in input xml rule
    pos_tags_from_input = get_pos_tag_dicts_from_rule(
        input_rule_xml,
        list(POS_MAPS.keys()),
    )

    # grab pos tags present in matching examples
    pos_tag_from_examples = [
        get_pos_tag_dicts_from_rule(r, POS_MAPS) for r in matching_examples
    ]
    pos_tag_from_examples = {k: v for d in pos_tag_from_examples for k, v in d.items()}

    # assemble POS list used in prompt from input and matching examples
    pos_tags = {**pos_tags_from_input, **pos_tag_from_examples}

    # TODO: include header in what is replaced to avoid empty header (similar to regex below)

    # 3. maybe regex
    def rule_has_regex(xml_string):
        return "postag_regexp=" in xml_string

    if rule_has_regex(input_rule_xml):
        regex_instructions = """
        II. Regular Expressions Used in Rules
        RX(.*?) A token that can be any word, punctuation mark, or symbol.
        RX([a-zA-Z]*) A token that can be any word.
        RX([a-zA-Z]+) A token that can be any word.
        """
        _replace_regex = regex_instructions
    else:
        _replace_regex = ""

    # 4. clean up xml
    def remove_message_and_short_tags(xml_string):
        # Remove content between <message> and </message> tags, including the tags
        xml_string = re.sub(
            r"\n<message>.*?</message>", "", xml_string, flags=re.DOTALL
        )
        # Remove content between <short> and </short> tags, including the tags
        xml_string = re.sub(r"\n<short>.*?</short>", "", xml_string, flags=re.DOTALL)
        return xml_string

    input_rule_xml = remove_message_and_short_tags(input_rule_xml)
    matching_examples = [remove_message_and_short_tags(r) for r in matching_examples]

    # 5. assemble prompt
    _replace_pos = "\n".join([f"{v}" for k, v in pos_tags.items()])
    _replace_matching_examples = "\n".join(matching_examples)
    system_prompt = PROMPT_TEMPLATE.format(
        example_rules=_replace_matching_examples,
        part_of_speech=_replace_pos,
        regex_rules=_replace_regex,
    )
    user_prompt = (
        "Input <pattern>:\n"
        + input_rule_xml
        + "\n\n"
        + "Are the <pattern> and Suggestion & Example of the XML rule a match? They are only a match if they are written EXACTLY how they should be. Yes or No. "
    )

    # include 'suggestion & example' in prompt
    user_prompt = user_prompt.replace(
        "</pattern>", "</pattern>\n        Suggestion & Example:"
    )

    # call model
    message = generate_simple_message(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    response, usage = call_gpt_with_backoff(
        model="gpt-4-1106-preview", messages=message, temperature=0
    )
    usages.append(usage)

    # check response and ask for correction if necessary
    if "yes" in response[:3].lower():
        return input_rule_xml, usages

    elif "no" in response[:3].lower():
        # rewrite suggestion and example tags
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": "No."},
            {
                "role": "user",
                "content": "Rewrite the <suggestion> and <example> tags to be correct:",
            },
        ]

        response_tags_rewrite, usage = call_gpt_with_backoff(
            messages=message,
            temperature=0,
            model="gpt-4-1106-preview",
        )
        usages.append(usage)

        # rewrite entire rule
        messages.extend(
            [
                {
                    "role": "assistant",
                    "content": response_tags_rewrite,
                },
                {
                    "role": "user",
                    "content": "Rewrite the entire rule including these modifications:",
                },
            ]
        )

        response_model_rule_rewrite, usage = call_gpt_with_backoff(
            messages=message,
            temperature=0,
            model="gpt-4-1106-preview",
        )
        usages.append(usage)

        # we think the following substitutes <suggestion> and <example> tags in the original rule with the corresponding tags from the model's response. sorry

        def replace_all_instances_of_tag(
            tag_label,
            src_rule_xml,
            target_rule_xml,
        ):
            """
            replace all instances of `<tag_label>` in `src_rule_xml` with the corresponding `<tag_label>` in `target_rule_xml`
            """

            def get_next_tag_instance(match):
                # tag_xml is an instance that matches `<tag_label>.*?</tag_label>`
                tag_xml = (
                    f"<{tag_label}>{match.group(1)}</{tag_label}>"
                    for match in re.finditer(
                        rf"<{tag_label}>(.*?)</{tag_label}>",
                        target_rule_xml,
                    )
                )
                return next(tag_xml, match.group(0))

            return re.sub(
                rf"<{tag_label}>.*?</{tag_label}>",
                get_next_tag_instance,
                src_rule_xml,
            )

        # replace all instances of <suggestion> tags in `input_rule_xml` with the corresponding <suggestion> tags in `response_model_rule_rewrite`
        new_rule_xml = replace_all_instances_of_tag(
            "suggestion",
            input_rule_xml,
            response_model_rule_rewrite,
        )

        # replace all instances of <example> tags in `new_rule_xml` with the corresponding <example> tags in `response_model_rule_rewrite`
        new_rule_xml = replace_all_instances_of_tag(
            "example",
            new_rule_xml,
            response_model_rule_rewrite,
        )

        return new_rule_xml, usages

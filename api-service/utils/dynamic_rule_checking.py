from typing import Dict, List, Tuple
from domain.dynamic_prompting.parts_of_speech import POS_MAPS
from domain.dynamic_prompting.prompt_leggo import (
    VALIDATE_RULE_PROMPT,
    REGEX_INSTRUCTIONS_PROMPT,
)
from utils.dynamic_prompting import (
    get_pos_tag_dicts_from_rule,
    remove_message_and_short_tags,
    rule_has_regex,
    replace_all_instances_of_tag,
)
from utils.logger import setup_logger
from utils.regexp_validation import post_process_xml
from utils.rule_similarity import get_similar_template_rules
from utils.example_tag_validation import validate_examples
from utils.utils import (
    call_gpt_with_backoff,
    generate_simple_message,
    remove_thought_tags,
)


dynamic_logger = setup_logger(__name__)


def check_rule_modification(input_rule_xml: str) -> Tuple[str, List[Dict]]:
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
    if rule_has_regex(input_rule_xml):
        _replace_regex = REGEX_INSTRUCTIONS_PROMPT
    else:
        _replace_regex = ""

    # 4. clean up xml
    input_rule_xml = remove_message_and_short_tags(input_rule_xml)
    matching_examples = [remove_message_and_short_tags(r) for r in matching_examples]

    # 5. assemble prompt
    _replace_pos = "\n".join([f"{v}" for k, v in pos_tags.items()])
    _replace_matching_examples = "\n".join(matching_examples)
    system_prompt = VALIDATE_RULE_PROMPT.format(
        example_rules=_replace_matching_examples,
        part_of_speech=_replace_pos,
        regex_rules=_replace_regex,
    )
    user_prompt = (
        "Input rule:\n"
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
        validated_rule_xml = input_rule_xml
    elif "no" in response[:3].lower():
        # rewrite suggestion and example tags
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": "No."},
            {
                "role": "user",
                "content": "Rewrite the <suggestion> and <example> tags to be correct. Think about what the example tag should be before writing it, paying special attention when placing <marker> tags. If the rule has an <antipattern>, make sure that there is one (and only one) <example> per <antipattern>. The <marker> tags **must** surround text that matches the pattern of the rule. Surround these thoughts in <thought> tags:",
            },
        ]

        response_tags_rewrite, usage = call_gpt_with_backoff(
            messages=messages, temperature=0, model="gpt-4-1106-preview", max_length=600
        )
        dynamic_logger.info(f"{response_tags_rewrite=}")
        response_tags_rewrite = remove_thought_tags(response_tags_rewrite)
        dynamic_logger.info(f"cleaned {response_tags_rewrite=}")
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
                    "content": "Rewrite the entire rule to include these modifications:",
                },
            ]
        )

        response_model_rule_rewrite, usage = call_gpt_with_backoff(
            messages=messages,
            temperature=0,
            model="gpt-4-1106-preview",
            max_length=1500,
        )
        dynamic_logger.info(f"{response_model_rule_rewrite=}")
        usages.append(usage)

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
        validated_rule_xml = new_rule_xml

    return validated_rule_xml, usages


def validate_modified_rule(xml: str) -> Tuple[str, List[Dict]]:
    usages = []
    # post process
    dynamic_logger.info("post processing: regexp validation")
    xml = post_process_xml(xml)
    dynamic_logger.info("post processing: validating example tags")
    xml, usage = validate_examples(xml)
    usages.extend(usage)
    dynamic_logger.info("post processing: catch all checker")
    xml, usage = check_rule_modification(xml)
    usages.extend(usage)
    return xml, usages

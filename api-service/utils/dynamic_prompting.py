import re
from domain.dynamic_prompting.parts_of_speech import POS_MAPS


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


def rule_has_regex(xml_string):
    return "postag_regexp=" in xml_string


def remove_message_and_short_tags(xml_string):
    # Remove content between <message> and </message> tags, including the tags
    xml_string = re.sub(r"\n<message>.*?</message>", "", xml_string, flags=re.DOTALL)
    # Remove content between <short> and </short> tags, including the tags
    xml_string = re.sub(r"\n<short>.*?</short>", "", xml_string, flags=re.DOTALL)
    return xml_string


def replace_all_instances_of_tag(
    tag_label,
    src_rule_xml,
    target_rule_xml,
):
    """
    replace all instances of `<tag_label>` in `src_rule_xml` with
    the corresponding `<tag_label>` in `target_rule_xml`.
    ~ sorry
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

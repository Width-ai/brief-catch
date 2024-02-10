import re


def get_tags_with_postag_regexp(xml):
    matchtag_pattern = r"<match.*?postag_regexp.*?>"
    tokentag_pattern = r"<token.*?postag_regexp.*?>"
    return re.findall(Rf"""({matchtag_pattern}|{tokentag_pattern})""", xml)


def get_postag_value(xml):
    return re.findall(r'postag="(.*?)"', xml)


def is_complex_regexp(s: str, model="gpt-4"):
    complex_tokens = [".*", ":", "|", "$"]
    for token in complex_tokens:
        if token in s:
            return True
    return False


def cleanup_postag_regexp(rule_xml):
    # 1. get relevant tags from xml
    tags = get_tags_with_postag_regexp(rule_xml)

    if len(tags) == 0:
        # no tags postag_regexp detected, nothing to do
        return rule_xml

    for ix in range(len(tags)):
        tag = tags[ix]
        # 2. get value of postag
        postag_value = get_postag_value(tag)
        assert (
            len(postag_value) <= 1
        ), f"expected only one postag value in enclosing tag, but got {postag_value}"

        # 3. if postag_value is not complex, remove postag_regexp
        if not is_complex_regexp(postag_value[0]):
            corrected_tag = re.sub(r'postag_regexp="yes" ', "", tag)
            rule_xml = re.sub(tag, corrected_tag, rule_xml)

    return rule_xml

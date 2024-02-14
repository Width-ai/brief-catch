import re


def get_tags_with_postag(xml):
    matchtag_pattern = r"<match.*?postag.*?>"
    tokentag_pattern = r"<token.*?postag.*?>"
    return re.findall(Rf"""({matchtag_pattern}|{tokentag_pattern})""", xml)


def get_postag_value(xml):
    return re.findall(r'postag="(.*?)"', xml)


def is_complex_regexp(s: str):
    complex_tokens = [".*", ":", "|", "$"]
    for token in complex_tokens:
        if token in s:
            return True
    return False


def validate_postag_regexp(xml):
    # 1. get tags with postag from xml
    tags = get_tags_with_postag(xml)

    if len(tags) == 0:
        # no tags with postag detected, nothing to do
        return xml

    for tag in tags:
        # 2. get value of postag
        postag_value = get_postag_value(tag)
        assert (
            len(postag_value) <= 1
        ), f"expected only one postag value in enclosing tag, but got {postag_value}"

        # 3. if postag_value is not complex, remove postag_regexp
        if is_complex_regexp(postag_value[0]):
            # ensure postag_regex=yes in complex postag values
            if 'postag_regexp="yes"' not in tag:
                corrected_tag = (
                    tag[: len("<token")] + ' postag_regexp="yes"' + tag[len("<token") :]
                )
                xml = xml.replace(tag, corrected_tag)
        else:
            # ensure postag_regex=yes in NOT present in simple postag values
            corrected_tag = re.sub(r'postag_regexp="yes" ', "", tag)
            xml = re.sub(tag, corrected_tag, xml)

    return xml


def validate_token_regexp(xml):
    # grab all token tags
    token_tags = re.findall(r"<token.*?>.*?</token>", xml)
    if len(token_tags) == 0:
        return xml
    for tag in token_tags:
        token_tag_value = re.findall(r"<token.*?>(.*?)</token>", xml)[0]
        if is_complex_regexp(token_tag_value):
            # ensure that regexp=yes is present in complex regexp
            if 'regexp="yes"' not in tag:
                corrected_tag = (
                    tag[: len("<token")] + ' regexp="yes"' + tag[len("<token") :]
                )
                # update xml
                xml = xml.replace(tag, corrected_tag)
        else:
            # ensure that regexp=yes is NOT present in simple regexp
            # NOTE: to want to remove space before XOR after
            patterns = [r'regexp="yes" ', r' regexp="yes"']
            corrected_tag = tag
            for p in patterns:
                corrected_tag = re.sub(p, "", corrected_tag)
            xml = re.sub(tag, corrected_tag, xml)
    return xml


def post_process_xml(xml):
    xml = validate_postag_regexp(xml)
    xml = validate_token_regexp(xml)
    return xml

import re
from typing import List
from utils.logger import setup_logger

logger = setup_logger(__name__)

def get_tags_with_postag(xml: str) -> List[str]:
    matchtag_pattern = r"<match.*?postag.*?>"
    tokentag_pattern = r"<token.*?postag.*?>"
    # TODO: exception tag?
    return re.findall(Rf"""({matchtag_pattern}|{tokentag_pattern})""", xml)


def get_postag_value(xml: str) -> List[str]:
    return re.findall(r'postag="(.*?)"', xml)


def is_complex_regexp(s: str):
    complex_tokens = [".*", ":", "|", "$", "[", "]", "+"]
    for token in complex_tokens:
        if token in s:
            return True
    return False


def validate_postag_regexp(xml: str) -> str:
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


def validate_token_regexp(xml: str) -> str:
    # grab all token tags
    token_tags = re.findall(r"<token.*?>.*?</token>", xml, flags=re.DOTALL)
    if len(token_tags) == 0:
        return xml

    for index, tag in enumerate(token_tags):
        # Handling exceptions: if there's an exception tag, skip regexp="yes" for the token tag
        exception_match = re.search(r"<exception>.*?</exception>", tag, flags=re.DOTALL)
        if exception_match:
            exception_content = exception_match.group(0)
            if is_complex_regexp(exception_content):
                if 'regexp="yes"' not in exception_content:
                    corrected_tag = exception_content.replace('<exception', '<exception regexp="yes"')
                    xml = xml.replace(exception_content, corrected_tag)
            else:
                # remove the attribute if not complex
                corrected_tag = exception_content.replace(' regexp="yes"', '')
                xml = xml.replace(exception_content, corrected_tag)
        
        # Extract the content of the token tag (re pull the tag after changing the original xml)
        tag = re.findall(r"<token.*?>.*?</token>", xml, flags=re.DOTALL)[index]
        token_content_match = re.search(r"<token.*?>.*?</token>", tag, flags=re.DOTALL)

        if token_content_match:
            token_content = token_content_match.group(0)
            exception_match = re.search(r"<exception.*?>.*?</exception>", token_content, flags=re.DOTALL)
            if exception_match:
                token_content = re.sub(r"<exception.*?>.*?</exception>", "", token_content)
            if is_complex_regexp(token_content):
                # ensure that regexp="yes" is present in complex regexp
                if 'regexp="yes"' not in tag:
                    corrected_tag = tag[:len("<token")] + ' regexp="yes"' + tag[len("<token"):]
                    xml = xml.replace(tag, corrected_tag)
            else:
                # ensure that regexp="yes" is NOT present in simple regexp
                token_open_tag = re.search(r"<token.*?>", tag, flags=re.DOTALL).group(0)
                corrected_open_tag = token_open_tag.replace(' regexp="yes"', '')
                corrected_tag = tag.replace(token_open_tag, corrected_open_tag)
                xml = xml.replace(tag, corrected_tag)
    return xml


def check_markers_in_examples(xml: str) -> str:
    examples = re.findall(r'<example.*?>.*?<\/example>', xml, flags=re.DOTALL)
    for example in examples:
        new_example = ""
        if 'correction=""' in example:
            new_example = example.replace('correction=""', "")
        if "<marker>" in example and 'correction="' not in example:
            new_example = example.replace("<marker>", "").replace("</marker>", "")
            xml = xml.replace(example, new_example)
    return xml


def post_process_xml(xml: str) -> str:
    xml = validate_postag_regexp(xml)
    xml = validate_token_regexp(xml)
    xml = check_markers_in_examples(xml)
    return xml

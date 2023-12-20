import re
from typing import List
from pattern.en import conjugate, PRESENT, PAST, PARTICIPLE, INFINITIVE, PROGRESSIVE, FUTURE, SG, PL


VERBS_THAT_NEED_HELP = ["center"]
PARTS_OF_SPEECH = ["VB", "NNS", "JJ", "V.*?", "VBG", "NN", "NN:U", "NN:UN", "NNP", "PRP.*", "N.*?", "JJ.*?", "IN", "CC", "DT", "EX", "LS", "MD", "POS", "RB", "RBR", "RBS", "UH"]
PUNCTUATIONS = [",", ";", ":", ".", "!", "?", "-"]


def split_rule_into_tokens(rule_text: str) -> List[str]:
    """
    Splits rules into tokens
    """
    tokens = []
    current_token = ''
    # counter to track the depth of nested parentheses
    depth = 0

    for char in rule_text:
        if char == '(':
            # Increase the depth counter when encountering an opening parenthesis
            depth += 1
            current_token += char
        elif char == ')':
            # Decrease the depth counter when encountering a closing parenthesis
            depth -= 1
            current_token += char
            if depth == 0:
                # If the depth is zero, we've closed a set of parentheses
                # Add the current token to the list and reset the current token
                tokens.append(current_token)
                current_token = ''
        elif char.isspace() and depth == 0:
            # If the character is a space and we're not within parentheses,
            # add the current token to the list (if it's not empty) and reset the current token
            if current_token:
                tokens.append(current_token)
                current_token = ''
        else:
            # For all other cases, add the character to the current token
            current_token += char
    if current_token:
        tokens.append(current_token)

    return tokens


def generate_verb_forms(verb: str) -> List[str]:
    if verb in VERBS_THAT_NEED_HELP:
        return [verb, f'{verb}ing', f'{verb}ed', f'{verb}s']
    # Initialize a set to store unique verb forms
    verb_forms = set()

    # Present tense for all persons and numbers
    for person in [1, 2, 3]:
        for number in [SG, PL]:
            verb_forms.add(conjugate(verb, tense=PRESENT, person=person, number=number))

    # Past tense for singular and plural
    verb_forms.add(conjugate(verb, tense=PAST, number=SG))
    verb_forms.add(conjugate(verb, tense=PAST, number=PL))

    # Other forms that do not vary by person or number
    verb_forms.add(conjugate(verb, tense=PARTICIPLE))  # been
    verb_forms.add(conjugate(verb, tense=INFINITIVE))  # be
    verb_forms.add(conjugate(verb, tense=PROGRESSIVE))  # being
    verb_forms.add(conjugate(verb, tense=FUTURE))       # will be

    verb_forms.discard(None)

    # Convert the set to a list and return it
    return list(verb_forms)


def generate_verb_forms_regex(base_verb: str) -> str:
    verb_forms = generate_verb_forms(base_verb)
    # Escape any regex special characters in the verb forms
    escaped_verb_forms = [re.escape(form) for form in verb_forms]
    # Join the verb forms with the regex 'or' operator (|) and wrap them in word boundaries (\b)
    regex_pattern = r'\b(?:' + '|'.join(escaped_verb_forms) + r')\b'
    return regex_pattern


def generate_excluded_words_pattern(excluded_words: List[str]) -> str:
    # Escape each word and join them into a regex alternation pattern
    excluded_pattern = '|'.join(map(re.escape, excluded_words))
    # Construct the negative lookahead pattern
    return r'(?!' + excluded_pattern + r'\b)'


def generate_special_token_regex(token: str) -> str:
    """
    Generate the regex representation for special tokens.
    """
    if token.startswith("RX("):
        # Handle RX tokens with custom regex patterns
        rx_content = re.search(r'RX\((.*?)\)', token).group(1)
        return rx_content
    elif token == "RB_SENT":
        # Handle adverbial phrase starting a sentence
        return r'(?:\b\w+\b, )'
    elif token == "SENT_END":
        # Handle the end of a sentence
        return r'(?<=\w)[.!?]'
    elif token == "SENT_START":
        # Handle the start of a sentence
        return r'(?:^|\A|\n)'
    elif token == "PCT":
        # Handle punctuation marks
        return r'[.,;:…!?]'
    elif token == "CC":
        # Handle coordinating conjunction
        return r'\b(?:for|and|nor|but|or|yet|so)\b'
    elif token == "CD":
        # Handle cardinal number
        # This regex matches simple numbers, compound numbers like "twenty-one", and numeric formats like "1,234"
        return r'\b(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|' \
               r'eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|' \
               r'eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|' \
               r'eighty|ninety|hundred|thousand|million|billion|trillion)' \
               r'(?:[-\s](?:one|two|three|four|five|six|seven|eight|nine|ten|' \
               r'eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|' \
               r'eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|' \
               r'eighty|ninety|hundred|thousand|million|billion|trillion))*' \
               r'|\d{1,3}(?:,\d{3})*(?:\.\d+)?)\b'
    else:
        # Default to escaping the token
        return re.escape(token)


def search_for_adhoc(adhoc_rule: str) -> List[str]:
    """
    Takes in an adhoc rule, splits the different tokens, then creates a regex to search for matches.
    """
    regex_pieces = []
    tokens = split_rule_into_tokens(adhoc_rule)
    for token in tokens:
        token = token.strip()
        part_of_speech_handled = False
        if token.startswith("CT("):
            # Conjugated verb
            find_verb_pattern = r'CT\((.*?)\)'
            verb_match = re.search(find_verb_pattern, token).group(1)
            regex_pieces.append(generate_verb_forms_regex(verb_match))
        elif token.startswith("(") and token.endswith(")"):
            # Options: create a regex string that has each value in the parentheses as an option
            # Remove the parentheses
            inner_content = token[1:-1]
            # Split the options by space
            options = inner_content.split()
            # Process each option
            option_patterns = []
            excluded_words = []
            for option in options:
                if option.startswith("CT("):
                    # Handle conjugated verbs within options
                    find_verb_pattern = r'CT\((.*?)\)'
                    verb_match = re.search(find_verb_pattern, option).group(1)
                    option_patterns.append(generate_verb_forms_regex(verb_match))
                elif option in PARTS_OF_SPEECH and not part_of_speech_handled:
                    # Replace part-of-speech abbreviations with a regex pattern for any word
                    option_patterns.append(r'\b\w+\b')
                    part_of_speech_handled = True
                elif option.startswith("!"):
                    # Add the word (without the "!") to the list of excluded words
                    excluded_words.append(option[1:])
                elif option == "~":
                    # we don't want to include this in the pattern
                    pass
                else:
                    # Handle special tokens or escape regular options
                    option_patterns.append(generate_special_token_regex(option))
            if excluded_words:
                excluded_words_pattern = generate_excluded_words_pattern(excluded_words)
                option_patterns = [
                    f"{excluded_words_pattern}{pattern}"
                    for pattern in option_patterns
                ]
            if "~" in options:
                # If the tilde is present, make the entire group optional
                options_pattern = r'(?: (?:' + '|'.join(option_patterns) + r'))?'
            else:
                # Join the processed options with the regex 'or' operator (|)
                options_pattern = r'(?:' + '|'.join(option_patterns) + r')'
            regex_pieces.append(options_pattern)
        elif token == "TO":
            regex_pieces.append(r'\bto\b')
        elif token in PUNCTUATIONS:
            # Handle punctuation without word boundaries
            regex_pieces.append(re.escape(token))
        elif token in ["SENT_START", "SENT_END", "PCT", "RB_SENT"] or token.startswith("RX("):
            # Handle special tokens
            regex_pieces.append(generate_special_token_regex(token))
        elif token in PARTS_OF_SPEECH:
            regex_pieces.append(r'\b\w+\b')
        else:
            # Single word: create a regex pattern that matches the word as a whole word
            word_pattern = r'\b' + re.escape(token) + r'\b'
            regex_pieces.append(word_pattern)
    return regex_pieces



def process_pattern(pattern_text: str) -> str:
    """
    Some post processing needed before rule will work correctly
    """
    if pattern_text.startswith("(?:^|\\A|\\n) "):
        pattern_text = pattern_text.replace("(?:^|\\A|\\n) ", "(?:^|\\A|\\n)")
    for punc in PUNCTUATIONS:
        pattern_text = pattern_text.replace(f" {punc}", punc)
    pattern_text = pattern_text.replace(" (?: (?:", "(?: (?:")
    pattern_text = pattern_text.replace("(?:“|“) ", "(?:“|“)")
    return pattern_text



def create_correction_regex(rule_pattern: str, corrections: str) -> List[str]:
    """
    Translate corrections into regex strings based on the rule it is associated with
    """
    # generate the tokens for the rule pattern
    rule_pattern_tokens = search_for_adhoc(rule_pattern)
    
    # split the correction pattern if multiple exist
    corrections = corrections.split("@")
    corrections = [pattern.strip() for pattern in corrections]

    correction_patterns = []
    for pattern in corrections:
        # isolate each token in the correction
        correction_tokens = pattern.split(" ")
        correction_tokens = [token.strip() for token in correction_tokens]
        correction_pattern = []
        for token in correction_tokens:
            if token.startswith("$"):
                # this token just refers to a token in the original rule pattern
                if "-" in token:
                    token = token.split("-")[0]
                token_index = int(token[1:])
                correction_pattern.append(rule_pattern_tokens[token_index])
            elif "-$" in token:
                # this token looks for a conjugated version of a verb, matching the pattern
                # TODO: how do we know what the pattern form is?
                verb = token.split("-$")[0]
                correction_pattern.append(generate_verb_forms_regex(verb))
            else:
                # TODO: are there any other cases to handle?
                correction_pattern.append('\\b'+token+'\\b')
        correction_patterns.append(process_pattern(' '.join(correction_pattern)))
    
    return correction_patterns
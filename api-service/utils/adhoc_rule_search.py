import json
import pandas as pd
import re
import spacy
from typing import Dict, List, Tuple
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from pattern.en import conjugate, PRESENT, PAST, PARTICIPLE, INFINITIVE, PROGRESSIVE, FUTURE, SG, PL
from domain.ngram_prompts.prompts import (
    OPTIMIZED_GROUPING_PROMPT,
    OPTIMIZED_GROUPING_FOLLOW_UP
)
from utils.logger import setup_logger
from utils.utils import generate_simple_message, call_gpt_with_backoff, extract_json_tags


adhoc_logger = setup_logger(__name__)

nlp = spacy.load("en_core_web_sm")

VERBS_THAT_NEED_HELP = ["center"]
OTHER_VERBS_THAT_NEED_HELP = ["focus"]
PARTS_OF_SPEECH = sorted(
    ["VB", "NNS", "JJ", "V.*?", "VBG", "NN", "NN:U", "NN:UN", "NNP", "PRP.*", "N.*?", "JJ.*?", "IN", "CC", "DT", "EX", "LS", "MD", "POS", "RB", "RBR", "RBS", "UH"],
    key=len,
    reverse=True
)
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
    if verb in OTHER_VERBS_THAT_NEED_HELP:
        return [verb, f'{verb}ing', f'{verb}ed', f'{verb}es']
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



def create_regex_from_rule(adhoc_rule: str) -> List[str]:
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
                if options[0] == "VB":
                    # conjugate verbs to exclude
                    verbs_to_exclude = []
                    for word in excluded_words:
                        verbs_to_exclude.extend(generate_verb_forms(word))
                    excluded_words = verbs_to_exclude
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
    rule_pattern_tokens = create_regex_from_rule(rule_pattern)
    
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



def pos_tag(input_sentence: str) -> List[Tuple[str, str]]:
    """
    Using spaCy, tag the words given with their corresponding Parts of Speech. Returns a
    list of tuples with the word followed by its tag:
    
    [("running", "VB"), ("Kevin", "NNP")]
    """
    token_tags = []
    tokens = []
    for token in nlp(input_sentence):
        tokens.append(token.text)
        token_tags.append(token.tag_)
    return list(zip(tokens, token_tags))



def find_optional_tokens(rule: str) -> List[Dict]:
    """
    Identifies any optional token in an adhoc rule and returns the index and the options
    """
    tokens = split_rule_into_tokens(rule)
    optional_tokens = []
    for token_index, token in enumerate(tokens):
        if "~" in token:
            options = token.replace("~", "").split()[1:-1]
            optional_tokens.append({"index": token_index, "options": options})
    return optional_tokens



def _process_match(rule: str, tokens_to_check: List[Dict], optional_tokens: List[Dict], match: Dict) -> Dict:
    """
    Helper function used to process each match in parallel
    """
    # get the match text from the dictionary
    ngram = match.get("ngram")
    ngram_tokens = ngram.split()
    # tag each token in the match text
    pos_tags = pos_tag(ngram)
    temp_tokens_to_check = deepcopy(tokens_to_check)

    # create a regex pattern to line up where the rule needs to evaluate the match text
    regex_pattern = process_pattern(' '.join(create_regex_from_rule(rule)))
    match_obj = re.search(regex_pattern, ngram)
    token_start_index = 0
    if match_obj:
        span_start, _ = match_obj.span()
        token_start_index = len(ngram[:span_start].split())
        for token_being_checked in temp_tokens_to_check:
            token_being_checked["index"] += token_start_index

    # check if we have optional tokens in the match and if we do adjust the token indecies
    if optional_tokens:
        for optional_token in optional_tokens:
            index = optional_token.get("index")
            options = optional_token.get("options")
            if ngram_tokens[index + token_start_index] not in options:
                for token_being_checked in temp_tokens_to_check:
                    if token_being_checked["index"] > index + token_start_index:
                        token_being_checked["index"] -= 1

    # make sure everything matches up
    if all((pos_tags[token_being_checked["index"]][1] == token_being_checked["pos"]) or
           (not token_being_checked["required"] or
            (".*?" in token_being_checked["pos"] and pos_tags[token_being_checked["index"]][1].startswith(token_being_checked["pos"][:-3])))
           for token_being_checked in temp_tokens_to_check):
        return match
    return None



def filter_matches_on_pos_tag(rule: str, matches: List[Dict]) -> List[Dict]:
    """
    Filters matches from ngram to make sure they match the PoS tags provided in an adhoc rule

    Returns a list of filtered matches
    """
    # if the rule starts with a regex pattern to match anything, remove this from the rule
    # so that we can line up where the rest of the pattern matches in the ngram result
    if rule.startswith("SENT_START"):
        rule = rule[10:].strip()
    if rule.startswith("RX(.*?)"):
        rule = rule[7:].strip()

    # split the rule into tokens to check if we need to identify a POS tag
    rule_tokens = split_rule_into_tokens(rule)
    # we dont need to treat punctuations as separate token in this function
    rule_tokens = [token for token in rule_tokens if token not in PUNCTUATIONS]
    tokens_to_check = []
    for token_index, token in enumerate(rule_tokens):
        for pos in PARTS_OF_SPEECH:
            if pos in token:
                tokens_to_check.append({"index": token_index, "pos": pos, "required": "~" not in token})
                # Stop after the first (most specific) match
                break

    # if no tokens need to be checked, return all the matches
    if not tokens_to_check:
        return matches

    # create a list of optional tokens, we will use this to adjust any indicies later if they are not present
    optional_tokens = find_optional_tokens(rule)
    
    # start checking the matches
    checked_matches = []
    with ThreadPoolExecutor() as executor:
        # submit all matches to the executor
        future_to_match = {executor.submit(_process_match, rule, tokens_to_check, optional_tokens, match): match for match in matches}

        # collect the results from the futures as they are completed
        checked_matches = [future.result() for future in as_completed(future_to_match) if future.result() is not None]

    return checked_matches



def filter_suggestion_matches_on_pos_tag(suggestion_filter: str, suggestion_regex: str, matches: List[Dict]) -> List[Dict]:
    """
    Filters matches from ngram to make sure they match the PoS tags provided in an adhoc rule

    Returns a list of filtered matches
    """
    # if the rule starts with a regex pattern to match anything, remove this from the rule
    # so that we can line up where the rest of the pattern matches in the ngram result
    if suggestion_filter.startswith("SENT_START"):
        suggestion_filter = suggestion_filter[10:].strip()
    if suggestion_filter.startswith("RX(.*?)"):
        suggestion_filter = suggestion_filter[7:].strip()

    # split the rule into tokens to check if we need to identify a POS tag
    suggestion_tokens = split_rule_into_tokens(suggestion_filter)
    adhoc_logger.info(f"{suggestion_tokens=}")
    # we dont need to treat punctuations as separate token in this function
    suggestion_tokens = [token for token in suggestion_tokens if token not in PUNCTUATIONS]
    tokens_to_check = []
    for token_index, token in enumerate(suggestion_tokens):
        for pos in PARTS_OF_SPEECH:
            if pos in token:
                tokens_to_check.append({"index": token_index, "pos": pos, "required": "~" not in token})
                # Stop after the first (most specific) match
                break
    adhoc_logger.info(f"{tokens_to_check=}")
    # if no tokens need to be checked, return all the matches
    if not tokens_to_check:
        return matches

    # create a list of optional tokens, we will use this to adjust any indicies later if they are not present
    optional_tokens = find_optional_tokens(suggestion_filter)
    
    # start checking the matches
    checked_matches = []
    with ThreadPoolExecutor() as executor:
        # submit all matches to the executor
        future_to_match = {executor.submit(_process_match, suggestion_regex, tokens_to_check, optional_tokens, match): match for match in matches}

        # collect the results from the futures as they are completed
        checked_matches = [future.result() for future in as_completed(future_to_match) if future.result() is not None]

    return checked_matches



def truncate_ngram_dataset(dataset: List[Dict], top_n=50) -> Dict:
    """
    Takes in ngram dataset and only keeps the top_n records based on score
    """
    # make the list of dictionary a single dictionary
    dataset = {list(item.keys())[0]: item[list(item.keys())[0]] for item in dataset}
    # flatten the dataset
    flattened = []
    for word_key, ngrams in dataset.items():
        for ngram in ngrams:
            try:
                score = float(ngram['score'])
                flattened.append((word_key, ngram['ngram'], score))
            except ValueError:
                adhoc_logger.error(f"Error converting score to float for '{ngram['ngram']}': {ngram['score']}")
    
    # sort by score in descending order
    sorted_flattened = sorted(flattened, key=lambda x: x[2], reverse=True)
    
    # take the top_n records, or all records if there are less than top_n
    top_records = sorted_flattened[:min(top_n, len(sorted_flattened))]
    
    # recreate the dataset with only the top records
    top_dataset = {}
    for word, ngram, score in top_records:
        if word not in top_dataset:
            top_dataset[word] = []
        top_dataset[word].append({'ngram': ngram, 'score': str(score)})
    
    return top_dataset



def rank_records_by_score(data: Dict) -> Dict:
    # Check if 'reranking' is in the dictionary and is a list
    for i, group in enumerate(data['reranking']):
        data['reranking'][i] = sorted(group, key=lambda x: float(x['score']), reverse=True)
    return data



def generate_suggestion_filters(rule: str, suggestions: str) -> List[str]:
    """
    Generate filters for suggestions using the rules. This is needed when a suggestion
    references a token in the rule that contains a POS tag.
    """
    rule_tokens = split_rule_into_tokens(rule)
    suggestion_filters = []
    for suggestion in suggestions.split("@"):
        suggestion_filter = []
        suggestion_tokens = split_rule_into_tokens(suggestion.strip())
        for suggestion_token in suggestion_tokens:
            if "$" in suggestion_token:
                suggestion_token = rule_tokens[int(suggestion_token.split("-")[0][1:])]
            suggestion_filter.append(suggestion_token)
        suggestion_filters.append(' '.join(suggestion_filter))
    return suggestion_filters




def ngram_helper_rule(rule_pattern: str) -> Dict:
    """
    Helper function to perform the ngram analysis on rule patterns
    """
    try:
        search_pattern = " ".join(create_regex_from_rule(rule_pattern))
        # load the csv with ngram data
        df = pd.read_csv("data/Ngram Over 1 score.csv")
        df.drop(columns=["Unnamed: 2", "Unnamed: 3", "Unnamed: 4"], inplace=True)
        df.dropna(inplace=True)
        
        # search the ngram data for the different patterns
        ngram_data = []
        flags = []
        clusters = []
        usages = []
        records = df[df['ngram'].str.contains(search_pattern)].to_dict(orient='records')

        # filter results from ngram
        records = filter_matches_on_pos_tag(rule_pattern, records)
        if records:
            ngram_data.append({rule_pattern: records})
        else:
            flags.append(rule_pattern)
        
        # drop any record not in the top n (default is 50)
        ngram_data = truncate_ngram_dataset(ngram_data)
        
        if ngram_data:
            # segment the results into groups with similar patterns
            grouping_messages = generate_simple_message(
                system_prompt=OPTIMIZED_GROUPING_PROMPT,
                user_prompt=json.dumps(ngram_data))
            grouping_output, grouping_usage = call_gpt_with_backoff(
                messages=grouping_messages,
                model="gpt-4-1106-preview",
                temperature=0,
                max_length=1750)
            usages.append(grouping_usage)
            grouping_messages.append({"role": "assistant", "content": grouping_output})
            grouping_messages.append({"role": "user", "content": OPTIMIZED_GROUPING_FOLLOW_UP})
            clusters_output, clusters_usage = call_gpt_with_backoff(
                messages=grouping_messages,
                model="gpt-4-1106-preview",
                temperature=0,
                max_length=1750)
            usages.append(clusters_usage)
            cleaned_cluster_output = extract_json_tags(clusters_output)
            clusters = json.loads(cleaned_cluster_output)
        return {
            "clusters": clusters,
            "flags": flags,
            "usages": usages
        }
    except Exception as e:
        adhoc_logger.error(f"Error clustering ngram data for pattern: {e}")
        adhoc_logger.exception(e)
        raise e



def ngram_helper_suggestion(rule_pattern: str, suggestion_pattern: str) -> Dict:
    """
    Helper function to perform the ngram analysis on suggestion patterns
    """
    try:
        suggestion_patterns = suggestion_pattern.split("@")
        search_patterns = create_correction_regex(rule_pattern, suggestion_pattern)
        adhoc_logger.info(f"{search_patterns=}")
        # load the csv with ngram data
        df = pd.read_csv("data/Ngram Over 1 score.csv")
        df.drop(columns=["Unnamed: 2", "Unnamed: 3", "Unnamed: 4"], inplace=True)
        df.dropna(inplace=True)
        
        # create suggestion filters
        suggestion_filters = generate_suggestion_filters(rule_pattern, suggestion_pattern)
        adhoc_logger.info(f"{suggestion_filters=}")

        # search the ngram data for the different patterns
        ngram_data = []
        flags = []
        clusters = []
        usages = []
        for index, search_pattern in enumerate(search_patterns):
            if search_pattern:
                records = df[df['ngram'].str.contains(search_pattern)].to_dict(orient='records')
                # filter results from ngram
                records = filter_suggestion_matches_on_pos_tag(suggestion_filters[index], search_pattern, records)
                if records:
                    ngram_data.append({suggestion_patterns[index].strip(): records})
                else:
                    flags.append(suggestion_patterns[index].strip())
        
        # drop any record not in the top n (default is 50)
        ngram_data = truncate_ngram_dataset(ngram_data)
        
        if ngram_data:
            # segment the results into groups with similar patterns
            grouping_messages = generate_simple_message(
                system_prompt=OPTIMIZED_GROUPING_PROMPT,
                user_prompt=json.dumps(ngram_data))
            grouping_output, grouping_usage = call_gpt_with_backoff(
                messages=grouping_messages,
                model="gpt-4-1106-preview",
                temperature=0,
                max_length=1750)
            usages.append(grouping_usage)
            grouping_messages.append({"role": "assistant", "content": grouping_output})
            grouping_messages.append({"role": "user", "content": OPTIMIZED_GROUPING_FOLLOW_UP})
            clusters_output, clusters_usage = call_gpt_with_backoff(
                messages=grouping_messages,
                model="gpt-4-1106-preview",
                temperature=0,
                max_length=1750)
            usages.append(clusters_usage)
            cleaned_cluster_output = extract_json_tags(clusters_output)
            clusters = json.loads(cleaned_cluster_output)
        return {
            "clusters": clusters,
            "flags": flags,
            "usages": usages
        }
    except Exception as e:
        adhoc_logger.error(f"Error clustering ngram data for suggestion: {e}")
        adhoc_logger.exception(e)
        raise e
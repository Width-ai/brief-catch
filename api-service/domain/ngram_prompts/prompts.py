POS_TAGGING_SYSTEM_MESSAGE = """You are an expert at Part of Speech Tagging. Using conventional abbreviations, return a corresponding list of Parts of Speech for the input tokens

Here is an example for your guidance, follow the output format exactly

Input:
['they', 'really', 'tend', 'to', 'run']
Output:
['PRP', 'RB', 'VBP', 'TO', 'VB']"""


OPTIMIZED_GROUPING_PROMPT = """Here is a list of patterns and records from a dataset where the field 'ngram' matched the pattern. Identify some ways we could group similar records from this list. For instance, if given the pattern "CT(sleep) JJ" some matches might be 
[
  {
    'CT(sleep) JJ': [
      {'ngram': 'sleep soundly', 'score': '2.0'},
      {'ngram': 'he slept long', 'score': '2.6'},
      {'ngram': 'i slept poor last night', 'score': '1.9'},
      {'ngram': 'If you slept better,', 'score': '1.75'},
      {'ngram': 'I should sleep earlier,', 'score': '1.75'}
    ]
  }
]

We could then identify clusters of sub-patterns like:
(a) "PRP CT(sleep) JJ" which corresponds to phrases like "he slept long" and "I slept poor last night" and "if you sleep better"
(b) "CT(sleep) JJ" which just corresponds to "sleep soundly"
(c) "PRP MD CT(sleep) JJ" which just corresponds to "i should sleep earlier"


Here are some perfect examples of possible sub-patterns for the original pattern "CT(sleep) JJ":
- "MD CT(sleep) JJ"
- "PRP CT(sleep) JJ"
- "VBD CT(sleep) JJ"
- "RB/IN CT(be) JJ"
- "CC/IN CT(be) JJ"
- "CT(sleep) JJ ,"
- "CT(sleep) JJ ."


Here are some important rules to keep in mind while identifying sub-patterns:
1. Use POS abbreviations in the sub-pattern where applicable
2. Make sure the sub-patterns are not too broad, but be sure to include all the matches
3. If the original pattern contains a congugated verb "CT(<base verb>)", do not separate different tenses of the verb into different clusters
"""


OPTIMIZED_GROUPING_FOLLOW_UP = """Using these groups, return a List of JSON objects where each object has the field "pattern" that contains the group pattern and then a list "values" that has all of the matches and their scores for that particular group. Surround the JSON object like this:

<JSON>
[
  {
    ...
  }
]
</JSON>"""
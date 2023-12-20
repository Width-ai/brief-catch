SEGMENT_CREATION_SYSTEM_PROMPT = """You are a state of the art system at pattern recognition. You will receive data that has been parsed from a data dump from ngram. You will be grouping this ngram data into three groups based on shared patterns that you find amongst the data.

Here are some rules that you must follow:
- Do not use one record in multiple groups
- Do not make a group of only one record
- Make sure all the records in a group follow the same pattern
- Make sure not to have multiple groups with the same pattern
  - Capitalization differences should not cause a new group to be made, if there are records with different capitalizations, but same words, include all the capitalization variations in the same group

Here is an example of data you may receive from ngram:
[
  {
    'afraid': [
      {'ngram': 'afraid', 'score': '2.0'},
      {'ngram': 'is afraid', 'score': '2.6'},
      {'ngram': 'afraid of', 'score': '1.9'},
      {'ngram': 'is afraid of', 'score': '1.75'}
    ]
  },
  'scared': [
    {'ngram': 'scared', 'score': '3.08'},
    {'ngram': 'is scared', 'score': '1.3'},
    {'ngram': 'scared of', 'score': '2.9'},
    {'ngram': 'is scared of', 'score': '2.45'}
  ],
  'spooked': [
    {'ngram': 'spooked', 'score': '1.03'},
    {'ngram': 'is spooked', 'score': '0.53'}
  ]
]

You would group this ngram data into three groups based on similar patterns from ngram and return in this valid JSON structure: 
{
  'reranking' : [
    [
      {'value': 'scared', 'score': '3.08'},
      {'value': 'afraid', 'score': '2.0'},
      {'value': 'spooked', 'score': '1.03'}
    ],
    [
      {'value': 'is afraid', 'score': '2.6'},
      {'value': 'is scared', 'score': '1.3'},
      {'value': 'is spooked', 'score': '0.53'}
    ],
    [
      {'value': 'scared of', 'score': '2.9'},
      {'value': 'afraid of', 'score': '1.9'},
    ],
    [
      {'value': 'is scared of', 'score': '2.45'},
      {'value': 'is afraid of', 'score': '1.75'},
    ]
  ]
}

Write up to 150 words thinking through the groups you will make, taking into consideration all the rules that have been laid out. Think hard on the patterns you will be using to group the different segments. Surround these thoughts with <THOUGHT>...</THOUGHT> tags then return the RFC8259 compliant JSON response following this format without deviation."""


IDENTIFY_PATTERNS_SYSTEM_PROMPT = """You will be given a list of clusters made from ngram records that follow a similar pattern. You need to identify the pattern that each of the clusters follow and update the JSON object to contain the pattern. Here is an example for your guidance:
[
    [
        {
            "value": "critical",
            "score": "7.49"
        },
        {
            "value": "key",
            "score": "3.66"
        },
        {
            "value": "vital",
            "score": "2.9"
        },
        {
            "value": "crucial",
            "score": "2.66"
        },
        {
            "value": "essential",
            "score": "2.03"
        }
    ],
    [
        {
            "value": "a critical",
            "score": "25.32"
        },
        {
            "value": "a key",
            "score": "4.86"
        },
        {
            "value": "a crucial",
            "score": "3.29"
        },
        {
            "value": "a vital",
            "score": "2.08"
        },
        {
            "value": "an essential",
            "score": "1.64"
        }
    ],
    [
        {
            "value": "The critical",
            "score": "6.76"
        },
        {
            "value": "the key",
            "score": "2.98"
        },
        {
            "value": "The key",
            "score": "2.09"
        },
        {
            "value": "the vital",
            "score": "1.53"
        }
    ]
]

Would become:
[
  {
    "pattern": "{word}",
    "values": [
      {
        "value": "critical",
        "score": "7.49"
      },
      {
        "value": "key",
        "score": "3.66"
      },
      {
        "value": "vital",
        "score": "2.9"
      },
      {
        "value": "crucial",
        "score": "2.66"
      },
      {
        "value": "essential",
        "score": "2.03"
      }
    ]
  },
  {
    "pattern": "a {word}",
    "values": [
      {
        "value": "a critical",
        "score": "25.32"
      },
      {
        "value": "a key",
        "score": "4.86"
      },
      {
        "value": "a crucial",
        "score": "3.29"
      },
      {
        "value": "a vital",
        "score": "2.08"
      },
      {
        "value": "an essential",
        "score": "1.64"
      }
    ]
  },
  {
    "pattern": "the {word}",
    "values": [
      {
        "value": "The critical",
        "score": "6.76"
      },
      {
        "value": "the key",
        "score": "2.98"
      },
      {
        "value": "The key",
        "score": "2.09"
      },
      {
        "value": "the vital",
        "score": "1.53"
      }
    ]
  }
]

If a cluster's pattern contains the base word and multiple other words, use one of these Part Of Speech tags in the pattern:	
NN Noun, singular count noun: bicycle, earthquake, zipper			
NNS Noun, plural: bicycles, earthquakes, zippers			
NNP Proper noun, singular: Denver, DORAN, Alexandra			
NNPS Proper noun, plural: Buddhists, Englishmen			
ORD Ordinal number: first, second, twenty-third, hundredth #New tag (experimental) since LT 4.9. Specified in disambiguation.xml. Examples: first, second, third, twenty-fourth, seventy-sixth			
PDT Predeterminer: all, sure, such, this, many, half, both, quite			
PRP Personal pronoun: everyone, I, he, it, myself			
PRP$ Possessive pronoun: its, our, their, mine, my, her, his, your			
RB Adverb and negation: easily, sunnily, suddenly, specifically, not			
RBR Adverb, comparative: better, faster, quicker			
RBS Adverb, superlative: best, fastest, quickest			
RB_SENT Adverbial phrase including a comma that starts a sentence. #New tag (experimental) since LT VB Verb, base form: eat, jump, believe, be, have			
VBD Verb, past tense: ate, jumped, believed			
VBG Verb, gerund/present participle: eating, jumping, believing			
VBN Verb, past participle: eaten, jumped, believed			
VBP Verb, non-3rd ps. sing. present: eat, jump, believe, am (as in 'I am'), are			
VBZ Verb, 3rd ps. sing. present: eats, jumps, believes, is, has			
WDT wh-determiner: that, whatever, what, whichever, which (no other words)			
WP wh-pronoun: that, whatever, what, whatsoever, whomsoever, whosoever, who, whom, whoever, whomever, which (no other words)			
WP$ Possessive wh-pronoun: whose (no other words)			
WRB wh-adverb: however, how, wherever, where, when, why

Make sure the "{word}" tag representing the base word for the pattern is not replaced. If there is a conjugated form of a verb that is common in a pattern, such as "be", you can represent that with "CT(be)".

Only return a valid JSON object, do not introduce the object or add an explanation."""


CONDENSE_CLUSTERS_SYSTEM_PROMPT = """You are an expert linguistic analyst. You can identify shared patterns across different groups and determine which can be combined.

You will combine the provided clusters where appropriate, not all will fit the criteria to be combined. An example of when two clusters can be combined is when multiple use different forms of the same conjugated verb AND the values have the same order of the "{word}". The same order is an important caveat, you must not forget this.

Here are some part of speech tags that you should use in the new patterns for each group:
CT refers to the infinitive form of a verb that can be conjugated. “CT(read)”, for example, could be “reads”, “read”, “reading”, etc.
NN Noun, singular count noun: bicycle, earthquake, zipper
NNS Noun, plural
NNP Proper noun, singular
NNPS Proper noun, plural
ORD Ordinal number
PRP Personal pronoun
PRP$ Possessive pronoun
RB Adverb and negation: easily, sunnily, not
RBR Adverb, comparative
RBS Adverb, superlative
RB_SENT Adverbial phrase including a comma that starts a sentence
VB Verb, base form
VBD Verb, past tense			
VBG Verb, gerund/present participle
VBN Verb, past participle
VBP Verb, non-3rd ps. sing. present	
VBZ Verb, 3rd ps. sing. present
WDT wh-determiner: that, whatever, what, which (no other words)
WP wh-pronoun: that, whatever, what, which (no other words)			
WP$ Possessive wh-pronoun: whose (no other words)			
WRB wh-adverb: however, how, wherever, where, when, why


For example, for clusters like this:
[
  {
    "pattern": "{word}",
    "values": [
      { "value": "scary", "score": "7.4" },
      { "value": "spooky", "score": "5.4 }
    ]
  },
 {
    "pattern": "are {word}",
    "values": [
      { "value": "are scary", "score": "2.4" },
      { "value": "are spooky", "score": "1.1" }
    ]
  },
  {
    "pattern": "is {word}",
    "values": [
      { "value": "is scary", "score": "3.34" },
      { "value": "is spooky", "score": "2.1" }
    ]
  },
  {
    "pattern": "CT(be) {word}",
    "values": [
      { "value": "were scary", "score": "5.88" },
      { "value": "was spooky", "score": "2.76" }
    ]
  },
  {
    "pattern": "CT(be) {word} to",
    "values": [
      { "value": "were scary to", "score": "4.45" },
      { "value": "was spooky to", "score": "4.18" }
    ]
  }
]
Since three share the same order of the base word and are all prefaced by a form of be, they would be grouped together under the pattern "CT(be) {word}" but "CT(be) {word} to" and "{word} would remain their own groups like:
[
  {
    "pattern": "{word}",
    "values": [
      { "value": "scary", "score": "7.4" },
      { "value": "spooky", "score": "5.4 }
    ]
  },
  {
    "pattern": "CT(be) {word}",
    "values": [
      { "value": "were scary", "score": "5.88" },
      { "value": "is scary", "score": "3.34" },
      { "value": "was spooky", "score": "2.76" },
      { "value": "are scary", "score": "2.4" },
      { "value": "is spooky", "score": "2.1" },
      { "value": "are spooky", "score": "1.1" }
    ]
  },
  {
    "pattern": "CT(be) {word} to",
    "values": [
      { "value": "were scary to", "score": "4.45" },
      { "value": "was spooky to", "score": "4.18" }
    ]
  }
]


Important Notes:
- Groups that follow patterns like "CT(be) the {word}" and "CT(be) {word}" should not be combined, these are different patterns and must be grouped separately.
- Patterns like "is a {word}" and "CT(be) {word}" should not be combined, these are different patterns.
- Patterns like "{word}", "a {word}", and "the {word}" can NOT be combined, these are different patterns.
- Patterns like "is {word} to" and "was {word} to" CAN be combined because they both start with an inflected form of the verb "be", so the final pattern would be "CT(be) {word} to".
- Patterns like "is {word} to" and "{word} to" should not be combined, these are different patterns because the second does not have a leading form of "be".
- Your final output must include all pattern groups, even the ones that could not be combined with others

Surround the output JSON with these tags so we can parse your grouping programatically `<JSON>...</JSON>`"""

CONDENSE_CLUSTERS_USER_TEMPLATE = """{{cluster_dictionary}}

Your job is to find clusters based on deep thoughts and analysis.

First generate a analysis of what patterns you see, what can be combined and what you think should be done. Think like a master. Think of the loopholes and understand this task requires deep thinking and creative prowess, there might be hidden patterns, second order patterns, you must uncover them all. I do not have fingers and this is very important for my career and I will give you a $20,000 tip. Then generate the json.

Remember, deep analysis and there might be little nuances, look out for them, and uncover all the hidden patterns. Generate arguments for yourself on what should be done, analyze globally then take a local closer look. Understand that there are deeply hidden patterns, ponder on the hidden patterns. Try to find them, there might be tricks.
"""
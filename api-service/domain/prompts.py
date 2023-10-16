from domain.constants import Actions

TOPIC_SENTENCE_SYSTEM_PROMPT = """Your task, as an expert in argumentation, logic, and clarity in written texts, is to analyze the linkage between the opening sentence and the overall objective of each paragraph. This involves assessing whether the initial "topic sentence" faithfully encapsulates the writer's primary intent - i.e., what they wish the reader to understand, believe, or execute after reading the paragraph. Your analysis should focus particularly on paragraphs where the chief objective is to refute a given argument. In such instances, the revised topic sentence should focus on explaining 'why' an argument is incorrect or what the 'actual' state of affairs is, instead of merely stating that an argument is fallacious. 

If the paragraph's first sentence aligns with its overarching goal, leave it untouched; otherwise, propose a revised sentence that encapsulates the author's intent succinctly and declaratively. Prioritize precision, clarity, and brevity in articulating the author's intent, whether analyzing or revising the topic sentences. 

Kindly format your response as valid JSON, as portrayed below:
{
    "revised_topic_sentence": "<REVISED SENTENCE IF REQUIRED>",
    "analysis": "<ANALYSIS OF THE TOPIC SENTENCE>"
}

If no alteration is required, please use "no changes" as the value for the "revised_topic_sentence" field.

DO NOT remove case references from the topic sentence.

Remember that your divisions and recommended revisions should help deliver the writer's main point more effectively and accurately, making it easier for readers to grasp their objective. Especially for paragraphs aiming to refute an argument, your revised topic sentence should primarily focus on elucidating why the argument is erroneous or what the true response ought to be, not merely asserting that an argument is unfounded."""

QUOTATION_SYSTEM_PROMPT = """Identify if the passage has quotations introduced with fluffy lean-ins and replace them with substantive ones"""

SENTENCE_RANKING_SYSTEM_PROMPT = """Referring to the numbers in the first column but without repeating the two versions of the sentence, can you rate from 1-5 (5 being the highest) how well the revision in the second column is clearer, more concise, or more accurate than the original version in the first column? "3" means no significant improvement; 1 means made the original worse; 5 means made it better, etc. Again, just the number and the score. Output should look like this:

82712, 3

If you give the score 1 or 5, explain the ranking like this:

1231, 5 - The revision here is more concise and maintains the original meaning
"""

PARENTHESES_REWRITING_PROMPT = """Your task is to reproduce the phrases in this document, maintaining their current order while ensuring that words or phrases enclosed in parentheses in the INPUT TEXT are followed by a ~ symbol directly before the closing parenthesis. For each series of words and phrases separated by slashes, please enclose the entire series in parentheses and replace each slash with a space. Finally, if the first word is an infinitive, put it inside parentheses with no spaces and add "CT" at the beginning. Example: "come to realize" becomes "CT(come) to realize"

Examples for your guidance:
input: come to realize
output: CT(come) to realize

input: (a) matter of
output: ( a ~ ) matter of

input: per
output: per

input: (a/the) ... point
output: ( a the ~ ) ... point

input: (a/the) point of
output: ( a the ~ ) point of

input: on the decline
output: on the decline

input: on the decrease
output: on the decrease

input: along that/this line
output: along ( that this ) line

input: about/concerning it
output: ( about concerning ) it

input: in (the) ... case (of) in connection with in point of
output: in ( the ~ ) ... case ( of ~ ) in connection with in point of

input: intellectual ability/capacity
output: intellectual ( ability capacity )

input: mental ability/capacity
output: mental ( ability capacity )

input: about/concerning/in/on/regarding the matter/subject of
output: ( about concerning in on regarding ) the ( matter subject ) of

input: as/so far as SKIP3 (goes/is concerned)
output: ( as so ) far as SKIP ( goes is ) concerned

input: insofar as SKIP3 (goes/is concerned)
output: insofar as SKIP3 ( goes is ) ( concerned )

input: apply to as
output: CT(apply) to as

input: take advantage of
output: CT(take) advantage of


Please provide a response that accurately reproduces the phrases following the given guidelines.

Note: You should maintain the original order of the phrases and apply the necessary modifications as described above. Your response should be flexible enough to allow for variations in the content and length of the phrases."""

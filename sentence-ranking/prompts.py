SENTENCE_RANKING_SYSTEM_PROMPT = """Referring to the numbers in the first column but without repeating the two versions of the sentence, can you rate from 1-5 (5 being the highest) how well the revision in the second column is clearer, more concise, or more accurate than the original version in the first column? "3" means no significant improvement; 1 means made the original worse; 5 means made it better, etc. Again, just the number and the score. Output should look like this:

82712. 3

If you give the score 1 or 5, explain the ranking like this:

1231. 5 - The revision here is more concise and maintains the original meaning
"""

# Compressed the original prompt into text that is still understood by gpt-4
CONDENSED_SENTENCE_RANKING_SYSTEM_PROMPT = """Enc: Ref to 1st col nums, rate 1-5 (5 high) on rev clarity, conciseness, accuracy of 1st col. "3"=no major improvement; 1=worse; 5=better. Just num & score, e.g.,
82712. 3
For 1, 5, explain, e.g.,
1231. 5 - More concise, retains original meaning.
"""

USER_TEXT_EXAMPLES = [
    "1384	4	[a] message accompanied with the address signal is then received and converted from a first file format to a second file format.	[a] message accompanied by the address signal is then received and converted from a first file format to a second file format.					And, even though the district court knew that Juror No. 8's comments were prompted by questions, it nonetheless implicitly found her testimony to be credible.	And, even though the district court knew that Juror No. 8's comments reacted to questions, it nonetheless implicitly found her testimony to be credible.",
    "603	5	Further, as Justice Kelly discusses at length, the Legislature has acquiesced with our construction of MCL 691.1404 since the Hobbs decision, including our presumption of the statute's sole purpose.	Further, as Justice Kelly discusses at length, the Legislature has acquiesced in our construction of MCL 691.1404 since the Hobbs decision, including our presumption of the statute's sole purpose."
    "821 	5	This letter is prompted by David Osborne's October 6, 2008 letter to the Pueblo County Attorney.	This letter responds to David Osborne's October 6, 2008 letter to the Pueblo County Attorney.",
    "2528	11	Much of the concern centered around vaccines against diphtheria, tetanus, and pertussis (DTP), which were blamed for children's disabilities and developmental delays.	Much of the concern centered on vaccines against diphtheria, tetanus, and pertussis (DTP), which were blamed for children's disabilities and developmental delays.",
    "6495	11	But it also suggests that the Supreme Court recruits judges who are prepared to take a very critical view of the performance of lower courts.	But it also suggests that the Supreme Court recruits judges prepared a very critical view of the performance of lower courts.",
]
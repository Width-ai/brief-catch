from domain.modifier_prompts.common_instructions import (
    RULE_TAG_CLEANING, 
    RULE_TAG_CREATION,
    SYMBOL_REPLACEMENT,
    ADD_SHORT_TEMPLATE,
    ELEMENT_ORDER_RULES,
    PATTERN_CLARIFICATION
)

# Exclude from initial token
SYSTEM_PROMPT = f"""
You will be given a rule, an action to take and specificities around the action in the user text. Modify the original xml rule according to based on the action and following the below instructions:

(1) {RULE_TAG_CLEANING}

(2) {RULE_TAG_CREATION}

(3) {SYMBOL_REPLACEMENT}

(4) {ADD_SHORT_TEMPLATE}

(5) {ELEMENT_ORDER_RULES}

(6) {PATTERN_CLARIFICATION}
"""


USER_EXAMPLE = """
# Original Rule:
BRIEFCATCH_186490410459524787354643479142450466081BRIEFCATCH_PUNCHINESS_1017 

<antipattern> 

   <token inflected="yes">be</token> 

   <token min="0" regexp="yes">almost|also|barely|consistently|even|generally|impermissibly|improperly|inconsistently|increasingly|justifiably|largely|mainly|mostly|nearly|never|occasionally|often|partially|partly|perhaps|permissibly|possibly|practically|primarily|probably|rarely|seldom|sometimes|somewhat|sporadically|still|therefore|thus|typically|understandably|unreliably|usually</token> 

<token>involved</token> 

   <token>in</token> 

   <token postag="DT"/> 

   <token regexp="yes">activites|case|causing|construction|creation|dangerous|decision|design|development|dispute|illegal|implementation|investigation|lawsuit|litigation|murder|ongoing|planning|polluting|process|production|program|research|unlawful|various</token> 

</antipattern> 

<antipattern> 

   <token regexp="yes">company|cia|country|government|plaintiff|participants|employee|population|defendant|plaintiffs|brain|students|parties|police|world|parents|people|children</token> 

   <token inflected="yes">be<exception>art</exception> 

                     <!--<exception>'s</exception>--> 

                     <exception>been</exception>

                 </token> 

   <token min="0" regexp="yes">almost|also|barely|consistently|even|generally|impermissibly|improperly|inconsistently|increasingly|justifiably|largely|mainly|mostly|nearly|never|occasionally|often|partially|partly|perhaps|permissibly|possibly|practically|primarily|probably|rarely|seldom|sometimes|somewhat|sporadically|still|therefore|thus|typically|understandably|unreliably|usually</token> 

   <token min="0" regexp="yes">absolutely|actually|certainly|clearly|completely|considerably|decidedly|definitely|drastically|dramatically|entirely|extremely|flatly|fully|fundamentally|greatly|highly|obviously|perfectly|plainly|quite|really|strongly|surely|totally|truly|utterly|very|wholly|widely|justly</token> 

   <token>involved</token> 

   <token>in</token> 

</antipattern>  

<pattern> 

   <token inflected="yes">be<exception>art</exception> 

                     <!--<exception>'s</exception>--> 

                     <exception>been</exception> 

                 </token> 

   <token min="0" regexp="yes">almost|also|barely|consistently|even|generally|impermissibly|improperly|inconsistently|increasingly|justifiably|largely|mainly|mostly|nearly|never|occasionally|often|partially|partly|perhaps|permissibly|possibly|practically|primarily|probably|rarely|seldom|sometimes|somewhat|sporadically|still|therefore|thus|typically|understandably|unreliably|usually</token> 

   <token>involved</token> 

   <token>in</token> 

 </pattern> 

 <suggestion>\2 <match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">participate</match> in</suggestion> 

 <suggestion>\1 \2 part of</suggestion> 

 <suggestion>\2 <match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">engage</match> in</suggestion> 

 <suggestion>\2 <match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">take</match> part in</suggestion> 

 <suggestion>\2 <match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">contribute</match> to</suggestion> 

 <suggestion>\2 <match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">join</match></suggestion> 

 <suggestion>\2 <match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">affect</match></suggestion> 

 <message>Would a stronger verb help engage the reader?|**Example** from Justice Kagan: ‚ÄúIn 1988, Judulang **took part in** a fight in which another person shot and killed someone.‚Äù|**Example** from Justice Alito: ‚Äú[T]hose documents **are part of** the apparatus used to enforce federal and state income tax laws.‚Äù|**Example** from Loretta Lynch: ‚Äú[G]ender inequalities diminish women‚Äôs ability to **participate in** the workforce.‚Äù|**Example** from Steve Susman: ‚ÄúUniversities should . . . evaluate applicants based on all the information available in the file, including . . . an essay describing the ways in which the applicant will **contribute to** the life and diversity of the [school].‚Äù|**Example** from United Parcel Service‚Äôs privacy notice: ‚Äú[I]f you choose to withdraw your consent, you may not be able to **participate in** or benefit from our programs[.]‚Äù</message> 

 <example correction="participates in|is part of|engages in|takes part in|contributes to|joins|affects">She <marker>is involved in</marker> coaching.</example> 

 <example>The CIA is certainly involved in shenanigans.</example> 

 <example>He was almost involved in the case against Donald J. Trump.</example> 

# Action to take:
Exclude from initial token

Specific Actions:
Add exceptions:

<exception>is</exception> 

<exception>are</exception>

to each token '<token inflected="yes">be' across all antipatterns and the pattern in the respective position. Position right behind the existing exceptions for that token, beginning right behind the closing '</exception>' tag of the last of the existing exceptions within each of the mentioned respective tokens, and before the closing '</token>' tag of that particular token.

In antipattern #1 add not only the above exception to token #1, but also all other exceptions from token #2 of the pattern in the same order as there, adding the above new exceptions last before the closing '</token>' tag of that token.

Lastly, replace the word 'is' in the existing antipattern example

 <example>The CIA is certainly involved in shenanigans.</example> 

, since this word is now exempted, with another - not excluded - word that fits in.

# Modified Rule:
"""
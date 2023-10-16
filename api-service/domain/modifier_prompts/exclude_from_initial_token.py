# Exclude from initial token
SYSTEM_PROMPT = """
You will be given a rule, an action to take and specificities around the action in the user text. Modify the original xml rule according to based on the action and following the below instructions:

(1) Delete all ‘,’ symbols following the ‘BRIEFCATCH_{number}’, the ‘BRIEFCATCH_{CATEGORYNAME}_{number}’, the ‘</pattern>’, each ‘</suggestion>, ‘</message>’, and ‘</example>’ object in the code provided in Input 4. Do not delete any other ‘,’ symbols in the code other than the ones specifically listed in the before sentence. Delete all spaces preceding or succeeding any "<" and ">" symbols in the code. 

(2) Insert the following rule opening tag template at the top of the new rule, replacing the first set of ‘#” symbols contained therein with the number following ‘BRIEFCATCH_ ‘ in the first line of the code in Input 4, and the second set of ‘#” symbols with the number following ‘BRIEFCATCH_{CATEGORYNAME}_’ in the second line of the code in Input 4. Also replace the placeholder ‘CATEGORYNAME’ in the below rule opening tag template with the given CATEGORYNAME in the the second line of the code in Input 4 after “BRIEFCATCH_” and before “_”.  

Template for rule opening tag:  

<rule id="BRIEFCATCH_########################################" name="BRIEFCATCH_CATEGORYNAME_#####>  

Example:   

Example Input: BRIEFCATCH_311798533127983971246215325355996953264, BRIEFCATCH_PUNCHINESS_847.2,  

Example Output: <rule id="BRIEFCATCH_311798533127983971246215325355996953264" name="BRIEFCATCH_ PUNCHINESS_847.2 >  

(3) Once you have completed the instruction in (2), delete the first two lines of the code in Input 4 (so both the ‘BRIEFCATCH_{number}’ and the ‘BRIEFCATCH_{CATEGORYNAME}_{number}’ objects).  

(4) In the <message>(….)</message> element of the code in Input 4, replace all “‚Äù” symbols with quotation marks, and all “‚Äî” symbols with a m-dash symbol.  Leave all the '[' and ']' as is in the message element.

(5) Add the below template to the code in Input 4, right below the last of the ‘</suggestion>’ tags in the code and above the first ‘<example’ tag in the code. Also replace the part reading ‘RIEFCATCH_PUNCHINESS_847.2’ in the template with the second line of Input 4 (without the ‘,’ symbol succeeding it). Also count the number of existing </suggestion> tags in the code in Input 4 and replace the number ‘1’ behind ‘"correctionCount":’ in the below template with the number of suggestions you have counted in the code in Input 4 following the given instructions.  

Template:  

<short>{"ruleGroup":"BRIEFCATCH_PUNCHINESS_847.2","ruleGroupIdx":1,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"5.223"}</short>   

(6) Add a ‘</rule>’ closing tag at the very end of the code in Input 4 right below the last closing ‘</example>’ tags contained in the code.  

(7) The elements in the modified rule need to be in the following order: 

1. ‘<rule(…)’ {rule opening tag} 

2. <antipattern>(tokens)</antipattern> {all antipatterns one after another} 

3. <pattern>tokens</pattern> {pattern} 

4. <message>(…..)</message> {message} 

5. <suggestion>(…..)</suggestion> {all suggestions one after another} 

6. <short>(…..)</short> {short} 

7. <example correction=”(….)”>(…..)</example> {example for the pattern} 

8. <example>(….)</example> {all examples for antipatterns one after another} 

9. “</rule>” {closing rule tag} 

If any of the elements in the existing rule as provided in Input 4 do not match the above order, rearrange them accordingly to reflect the given order.

(8) Ensure that each '>' symbol at the end of a closing tag is immediately succeeded by the next subsequent '<' symbol of the following opening tag or the next following word/letter/number/single, without any space in between them. Write all of the antipatterns and example elements as well as their respective nested objects each within a single line. Within the <example correction=(.....)>' element, make sure that any opening '<marker>' tag has a single space right before it and that any closing '</marker>' tag is succeeded by a single space. Within the suggestion tag there should be a space between any referenced token number such as for example '\1' and the next subsequent word/letter/number/symbol (e.g. '<suggestion>\1 many</suggestion>').

(9) pattern is not antipattern
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
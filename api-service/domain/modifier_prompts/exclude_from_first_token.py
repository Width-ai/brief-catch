# Exclude from first token
SYSTEM_PROMPT = """
You will be given a rule, an action to take and specificities around the action in the user text. Modify the xml rule according to the info provided in sections 1 and 2.

# Section 1:
Modify the xml according to the specific Actions

# Section 2:
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
"""

USER_EXAMPLE = """
# Original Rule:
BRIEFCATCH_199521758025408900899326796412516191904BRIEFCATCH_CONCISENESS_5808

<pattern>
<token regexp="yes">judgment|judgement</token>
<token>in</token>
<token>this</token>
<token regexp="yes">case|action|matter</token>
</pattern>
<suggestion>\1</suggestion>
<message>**In this matter** or **judgment** is usually implied when you refer to a particular dispute.|**Example** from Walter Dellinger: ‚Äú[T]he appropriate remedy would be to reverse the **judgment** and remand with instructions directing the district court to engage in appropriate fact-finding.‚Äù|**Example** from Shay Dvoretzky: ‚ÄúEven so, Petitioner claims that he did not know about **the judgment** until September 2014[.]‚Äù</message><example correction="judgment">Sought <marker>judgment in this case</marker>.</example>

# Action to take:
Exclude from first token

Specific Actions:
Delete the word option "case" from the final token of the pattern. Modify the example phrase in the example correction element accordingly so that it reflects the before change and matches the modified pattern.

# Modified Rule:
"""

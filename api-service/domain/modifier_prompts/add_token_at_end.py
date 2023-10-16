# Add token at end requiring one of these words
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
BRIEFCATCH_75803361340040807034346159244094965068 BRIEFCATCH_PUNCHINESS_621 

<antipattern> 

   <token>for</token> 

   <token>the</token> 

   <token case_sensitive="yes">protection</token> 

   <token>of</token> 

   <token regexp="yes">children|health|human|investors|public</token> 

 </antipattern> 

 <antipattern> 

   <token>or</token> 

   <token>for</token> 

   <token>the</token> 

   <token case_sensitive="yes">protection</token> 

   <token>of</token> 

 </antipattern> 

 <antipattern> 

   <token>,</token> 

   <token>for</token> 

   <token>the</token> 

   <token case_sensitive="yes">protection</token> 

   <token>of</token> 

 </antipattern>  

<pattern> 

   <token>for</token> 

   <token>the</token> 

   <token case_sensitive="yes">protection</token> 

   <token>of</token> 

 </pattern> 

 <message>Could you convert this **noun to a verb** here to strengthen the sentence?|**Example** from Justice Breyer: ‚ÄúOne side believes the right essential **to protect** the lives of those attacked in the home; the other side believes it essential to regulate the right in order to protect the lives of others attacked with guns.‚Äù|**Example** from John Quinn: ‚ÄúFinally, if this Court deems a preliminary injunction to be necessary, [Defendant] should post a bond **to protect** Defendant‚Äôs costs and damages if the injunction is improvidently granted.‚Äù|A **nominalization** is a noun created from a verb (such as **utilization** and **expansion**) or from an adjective (such as **applicability** and **safety**). |Changing **nominalizations** back to verbs often makes writing livelier.</message> 

<suggestion>to protect</suggestion> 

 <suggestion>for protecting</suggestion> 

 <example correction="to protect|for protecting">The court exercised its discretion <marker>for the protection of</marker> the jurors' privacy.</example> 

 <example>This was for the protection of children.</example> 

 <example>It was for this or for the protection of children.</example> 

 <example>But, for the protection of the plaintiff, we said no.</example> 

# Action to take:
add token at end requiring one of these words

Specific Actions:
Add the following token to the pattern as well as the as the second, third, and forth antipattern of the below xml rule as their final token, respectively:

<token regexp="yes">the|her|them|and|themselves|his|its|a</token> 

Delete first antipattern in the rule as well as the corresponding example element (" <example>This was for the protection of children.</example> ").

Add the new token #5 to the suggestions so that they read:

<suggestion>to protect \5</suggestion> 

<suggestion>for protecting \5</suggestion>

Modify the second last example phrase (' <example>It was for this or for the protection of the partner.</example> ') so that it matches the new modified antipattern it corresponds to.

# Modified Rule:
"""

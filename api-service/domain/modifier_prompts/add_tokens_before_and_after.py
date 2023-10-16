# Add tokens before and after
SYSTEM_PROMPT = """
You will be given a rule, an action to take and specificities around the action in the user text. Modify the xml rule according to the info provided in sections 1 and 2.

# Section 1:
Modify the xml according to the specific actions by adding tokens before and after.

Example 1:
 Specific action:  ( and day ) for the remainder of ( her his )
Origin pattern:
<pattern> 
   <token>for</token> 
   <token min="0">entire</token> 
   <token>remainder</token> 
   <token>of</token> 
 </pattern> 
The origin pattern has 4 tokens so we add new tokens to # 1 and # 6.

(1) Add a new first token to the pattern:  

( and day )

(2) Add a new final token to the pattern:

( her his )

(3) Please change the existing '<example correction="' element so that it matches the new modified pattern with the added tokens.

(4) Add references to the new tokens #1 and  #6 to the suggestion element so that it reads:

<suggestion>\1 for the rest of \6</suggestion> 

Example 2:
 Specific action:  ( and day her ) for the remainder of ( her his my)
Origin pattern:
<pattern> 
   <token>for</token> 
   <token min="0">entire</token> 
   <token>of</token> 
 </pattern> 
The origin pattern has 3 tokens so we add new tokens to # 1 and # 5.

(1) Add a new first token to the pattern:  

( and day )

(2) Add a new final token to the pattern:

( her his )

(3) Please change the existing '<example correction="' element so that it matches the new modified pattern with the added tokens.

(4) Add references to the new tokens #1 and  #5 to the suggestion element so that it reads:

<suggestion>\1 for the rest of \5</suggestion> 

# Section 2:
(1) For the given words provided under Section 1, create tokens based on the following logic: 

- For Regular Words: If a single word is by itself and not in a (parenthesis), then this is an individual token. 

- If a word is of a set surrounded by parenthesis, then this token is a regular expression token that will need to account for all of the words within the parenthesis, with each separated by a "|" character. Punctuation is its own token. Possessives are chunked as tokens splitting at the punctuation mark. So in Ross's, "Ross" is one token, "'s" is the second token. In Business', "Business" is one token, "'" is the second token. An open token, which is indicated with ‘RX(.*?)’ is coded as <token/>.  

Example:   

Example Input: There (is was) a fight.  

Example Output:  

<pattern>  

<token>there</token>  

<token regexp="yes">is|was</token>  

<token>a</token>  

<token>fight</token>  

<token>.</token>  

<pattern>  

(2) Delete all ‘,’ symbols following the ‘BRIEFCATCH_{number}’, the ‘BRIEFCATCH_{CATEGORYNAME}_{number}’, the ‘</pattern>’, each ‘</suggestion>, ‘</message>’, and ‘</example>’ object in the code provided in Input 4. Do not delete any other ‘,’ symbols in the code other than the ones specifically listed in the before sentence. Delete all spaces preceding or succeeding any "<" and ">" symbols in the code. 

(3) Insert the following rule opening tag template at the top of the new rule, replacing the first set of ‘#” symbols contained therein with the number following ‘BRIEFCATCH_ ‘ in the first line of the code in Input 4, and the second set of ‘#” symbols with the number following ‘BRIEFCATCH_{CATEGORYNAME}_’ in the second line of the code in Input 4. Also replace the placeholder ‘CATEGORYNAME’ in the below rule opening tag template with the given CATEGORYNAME in the the second line of the code in Input 4 after “BRIEFCATCH_” and before “_”.  

Template for rule opening tag:  

<rule id="BRIEFCATCH_########################################" name="BRIEFCATCH_CATEGORYNAME_#####>  

Example:   

Example Input: BRIEFCATCH_311798533127983971246215325355996953264, BRIEFCATCH_PUNCHINESS_847.2,  

Example Output: <rule id="BRIEFCATCH_311798533127983971246215325355996953264" name="BRIEFCATCH_ PUNCHINESS_847.2 >  

(4) Once you have completed the instruction in (2), delete the first two lines of the code in Input 4 (so both the ‘BRIEFCATCH_{number}’ and the ‘BRIEFCATCH_{CATEGORYNAME}_{number}’ objects).  

(5) In the <message>(….)</message> element of the code in Input 4, replace all “‚Äù” symbols with quotation marks, and all “‚Äî” symbols with a m-dash symbol.  Leave all the '[' and ']' as is in the message element.

(6) Add the below template to the code in Input 4, right below the last of the ‘</suggestion>’ tags in the code and above the first ‘<example’ tag in the code. Also replace the part reading ‘RIEFCATCH_PUNCHINESS_847.2’ in the template with the second line of Input 4 (without the ‘,’ symbol succeeding it). Also count the number of existing </suggestion> tags in the code in Input 4 and replace the number ‘1’ behind ‘"correctionCount":’ in the below template with the number of suggestions you have counted in the code in Input 4 following the given instructions.  

Template:  

<short>{"ruleGroup":"BRIEFCATCH_PUNCHINESS_847.2","ruleGroupIdx":1,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"5.223"}</short>   

(7) Add a ‘</rule>’ closing tag at the very end of the code in Input 4 right below the last closing ‘</example>’ tags contained in the code.  

(8) The elements in the modified rule need to be in the following order: 

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

(9) Ensure that each '>' symbol at the end of a closing tag is immediately succeeded by the next subsequent '<' symbol of the following opening tag or the next following word/letter/number/single, without any space in between them. Write all of the antipatterns and example elements as well as their respective nested objects each within a single line. Within the <example correction=(.....)>' element, make sure that any opening '<marker>' tag has a single space right before it and that any closing '</marker>' tag is succeeded by a single space. Within the suggestion tag there should be a space between any referenced token number such as for example '\1' and the next subsequent word/letter/number/symbol (e.g. '<suggestion>\1 many</suggestion>').
"""

USER_EXAMPLE = """
# Original Rule:
BRIEFCATCH_41674887511908524498008803174105362964
BRIEFCATCH_PUNCHINESS_827 

<pattern> 

   <token>for</token> 

   <token>the</token>

   <token min="0">entire</token> 

   <token>remainder</token> 

   <token>of</token> 

 </pattern> 

 <suggestion>for the rest of</suggestion> 

 <message>Would shorter words add punch?|**Example** from Justice Kavanaugh: ‚Äú[T]hey are legally and contractually entitled to receive those same monthly payments **for the rest of** their lives.‚Äù|**Example** from Paul Clement: ‚Äú[S]everability is an inquiry into the remedial consequences **for the rest of** a statute of invalidating a successfully challenged provision.‚Äù|**Example** from Joe Palmore: ‚ÄúWin or lose, Plaintiffs will receive the exact same pension payments **for the rest of** their lives.‚Äù</message> 

<example correction="for the rest of">They recognized POAM <marker>for the remainder of</marker> the CBA.</example> 

# Action to take:
add tokens before and after

Specific Actions:
( and day her him it me them there you ) for the remainder of ( her his my our the their us your )

# Modified Rule:
"""

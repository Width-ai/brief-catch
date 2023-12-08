# Antipatterns
from domain.modifier_prompts.common_instructions import STANDARD_PROMPT

SYSTEM_PROMPT = STANDARD_PROMPT

USER_EXAMPLE = """
# Original Rule:
BRIEFCATCH_176685406330453121692175320702356195004BRIEFCATCH_LEGALESE_2925 

 <antipattern> 

   <token inflected="yes" regexp="yes">govern</token> 

   <token>where</token> 

   <token regexp="yes">a|and|there|they|to|you</token> 

 </antipattern> 

 <antipattern> 

   <token inflected="yes" regexp="yes">apply</token> 

   <token>where</token> 

   <token regexp="yes">any|no|there</token> 

 </antipattern> 

<pattern> 

   <token inflected="yes" regexp="yes">govern|apply</token> 

   <token>where</token> 

 </pattern> 

 <suggestion>\1 when</suggestion> 

 <suggestion>\1 whether</suggestion> 

 <message>Would direct language convey your point just as effectively? If this is a condition, could you use **if** or **when** while reserving **where** for spaces and places?|**Example** from Justice Kagan: ‚Äú[I]f a court finds that a lawsuit . . . would have settled at a specific time‚Äîfor example, **when a party** was legally required to disclose evidence fatal to its position‚Äîthen the court . . . .‚Äù|**Example** from Lord Denning: ‚ÄúThere are cases in our books in which the courts will set aside a contract . . . **when the parties** have not met on equal terms‚Äî**when the one** is so strong in bargaining power and the other so weak‚Äîthat, as a matter of common fairness . . . .‚Äù</message> 

 <example correction="applies when|applies whether">The FTAIA‚Äôs general rule <marker>applies where</marker> the anticompetitive conduct at issue is foreign.</example> 

 <example>Governed where they landed.</example> 

 <example>Applied where any person does.</example> 

# Action to take:
add antipattern

Specific Actions:
( doctrine exception exemption it provision section this ) does not apply where

# Modified Rule:
"""

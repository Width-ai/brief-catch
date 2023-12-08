# Antipattern
from domain.modifier_prompts.common_instructions import STANDARD_PROMPT

SYSTEM_PROMPT = STANDARD_PROMPT

USER_EXAMPLE = """
# Original Rule:
BRIEFCATCH_112560687008026105902384280024186447379 BRIEFCATCH_PUNCHINESS_373.1 

<antipattern> 
 <token>so</token> 
 <token>numerous</token> 
</antipattern> 

 
<antipattern> 
 <token postag="RB.*" postag_regexp="yes"/> 
 <token>numerous</token> 
</antipattern> 

<pattern> 
 <token regexp="yes">[a-zA-Z]+ 
 <exception>less</exception> 
 <exception>more</exception> 
 <exception>very</exception> 
 <exception>extremely</exception> 
 <exception>totally</exception> 
 <exception>absolutely</exception> 
 <exception>incredibly</exception> 
 <exception>quite</exception> 
 <exception>rather</exception> 
 <exception>highly</exception> 
 <exception>really</exception> 
 <exception>most</exception> 
 <exception>be</exception> 
 </token> 
 <token min="0" regexp="yes">very|extremely|totally|absolutely|incredibly|quite|rather|highly|really</token> 
 <token>numerous</token> 
</pattern> 
<suggestion>\1 many</suggestion> 
<suggestion>\1 several</suggestion> 
<message>Would direct language or shorter words sound more confident and add punch?|**Example** from Justice Scalia: ‚Äú[T]he partner may . . . have acted in good faith . . . , which is a bar to the imposition of **many** penalties[.]‚Äù|**Example** from Justice Thomas: ‚Äú[Petitioner] is the assignee of **several** patents[.]‚Äù|**Example** from Justice Kagan: ‚ÄúAlong with its **many** tributaries, the river drains a 24,900-square-mile watershed[.]‚Äù|**Example** from Justice Sotomayor: ‚ÄúAlthough in **many** cases reasonable investors would not consider . . . .‚Äù|**Example** from Neal Katyal: ‚ÄúBut the electric-utility industry comprises **many** more companies in the United States and abroad[.]‚Äù|**Example** from Deanne Maynard: ‚ÄúThe . . . proceedings commenced in 1970 when the United States, acting on its own behalf and as trustee for **several** tribes, . . . .‚Äù|**Example** from John Quinn: ‚ÄúBoth the cases [Defendant] cites, and the **many** others it ignores, hold otherwise[.]‚Äù|**Example** from Kannon Shanmugam: ‚ÄúArbitration . . . offers **many** benefits over traditional litigation.‚Äù|**Example** from Kathleen Sullivan: ‚ÄúFor **many** broadcasters, the chilling effect is profound and discourages live programming altogether[.]‚Äù|**Example** from Office of Legal Counsel: ‚ÄúIn 1939, Congress placed the Social Security Board within . . . a now-defunct agency that supervised **several** government benefits programs.‚Äù</message> 
<example correction="on many|on several">served subpoenas <marker>on numerous</marker> agencies</example> 
<example>The errors were so numerous as to defeat understanding.</example> 
<example>Extremely numerous problems plagued the filings.</example>


# Action to take:
add antipattern

Specific Actions:
are numerous ( in studies reports )

# Modified Rule:
"""

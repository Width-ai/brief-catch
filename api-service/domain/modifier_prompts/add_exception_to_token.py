# Add exception to token
from domain.modifier_prompts.common_instructions import STANDARD_PROMPT

SYSTEM_PROMPT = STANDARD_PROMPT

USER_EXAMPLE = """
# Original Rule:
<rule id="BRIEFCATCH_147725296952682099987839530434290533040" name="PUNCHINESS_377">
<antipattern>
  <token regexp="yes">can|could|shall|should</token>
  <token>ascertain</token>
  </antipattern>
<antipattern>
  <token inflected="yes">ascertain</token>
  <token min="0" skip="5"/>
  <token regexp="yes">intent|meaning|standing|truth</token>
  </antipattern>
<antipattern>
  <token inflected="yes">ascertain</token>
  <token>the</token>
  <token>citizenship</token>
  </antipattern>
<antipattern>
  <token inflected="yes">ascertain</token>
  <token>their</token>
  </antipattern>
<antipattern>
  <token>ascertain</token>
  <token>whether</token>
</antipattern>
<pattern>
  <token inflected="yes">ascertain</token>
  </pattern>
<message>Would direct language convey your point just as effectively?|**Example** from Chief Justice Roberts: "The SEC . . . is not like an individual victim who relies on apparent injury to **learn of** a wrong."|**Example** from Judge Nalbandian: "The same day that her son lodged his complaints . . . , police . . . told her to come to the police station to **find out about** her son."|**Example** from Juanita Brooks: "In *Keystone*, after obtaining a patent, the patentee **learned of** a possible prior use of its invention."|**Example** from Jeff Lamken: "If the President **determined** that the SEC Commissioners were neglect¬≠ing their duty to regulate the securities markets, he could remove the Commissioners[.]"|**Example** from YouTube's terms of service: "Among other things, you can **find out about** YouTube Kids, the YouTube Partner Program . . . ."</message>
<suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">determine</match></suggestion>
<suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">learn</match></suggestion>
<suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">establish</match></suggestion>
<suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">discover</match></suggestion>
<suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">find</match> out</suggestion>
<suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">figure</match> out</suggestion>
<suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">decide</match></suggestion>
<suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">arrive</match> at</suggestion>
<suggestion><match no="1" postag="(V.*)" postag_regexp="yes" postag_replace="$1">learn</match> of</suggestion>
<short>{"ruleGroup":"BRIEFCATCH_PUNCHINESS_377","ruleGroupIdx":1,"isConsistency":false,"isStyle":true,"correctionCount":9,"priority":"5.223"}</short>
<example correction="determined|learned|learnt|established|discovered|found out|figured out|decided|arrived at|learned of|learnt of">She <marker>ascertained</marker> the item's whereabouts.</example>
<example>We can ascertain their intent from the examples provided</example>
<example>Ascertain its intent.</example>
<example>To ascertain the citizenship.</example>
<example>We couldn't ascertain their intent.</example>
<example>It is crucial to ascertain whether the facts are true.</example>
</rule>

# Action to take:
add antipattern

Specific Actions:
ascertain whether

Add exception '<exception>ascertaining</exception>' to the first token of the patten as well as the first token of the second, third, and fourth antipattern in the below xml rule, so that they each read:

<token inflected="yes">ascertain<exception>ascertaining</exception></token>

# Modified Rule:
"""

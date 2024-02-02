# note changed to dict below
TEMPLATE_RULES = [
    """
<rule id="{new_rule_id}" name="BRIEFCATCH_DIRECT_LANGUAGE_30116">
    <pattern>
        <token>
            <exception regexp="yes">abortion|anywhere|cases|chart|everywhere|used|violation</exception>
        </token>
        <token>except</token>
        <token>where</token>
        <token>
            <exception regexp="yes">noted|otherwise|permitted|specifically|such</exception>
        </token>
    </pattern>
    <suggestion><match no="1"/> unless <match no="4"/></suggestion>
    <example correction="examples unless they">Italic type is used for <marker>examples except where they</marker> are presented in lists.</example>
</rule>

""",
    """
<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30115">
    <pattern>
        <or>
            <token inflected="yes">be</token>
            <token>and</token>
        </or>
        <token>a</token>
        <token>bit</token>
        <token postag="JJ.*" postag_regexp="yes">
            <exception regexp="yes">more|much|of</exception>
        </token>
    </pattern>
    <suggestion><match no="1"/> <match no="4"/></suggestion>
    <example correction="was challenging">The project <marker>was a bit challenging</marker>.</example>
</rule>
""",
    """
<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30120">
        <pattern>
                <token regexp="yes">and|is</token>
                <token>not</token>
                <token>without</token>
                <token regexp="yes">consequence|consequences</token>
        </pattern>
        <suggestion><match no="1"/> significant</suggestion>
        <suggestion><match no="1"/> weighty</suggestion>
        <suggestion><match no="1"/> consequential</suggestion>
        <example correction="is significant|is weighty|is consequential">The event <marker>is not without consequence</marker>.</example>
</rule>
""",
]

# assign unique id to each template rule
TEMPLATE_RULES = {ix: r for ix, r in enumerate(TEMPLATE_RULES)}

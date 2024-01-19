import os
from dotenv import load_dotenv
load_dotenv()
from utils.utils import insert_into_pinecone

data = [
    {
        "id": "2e283c3b-449c-43d4-a280-9ca01669b66a",
        "embedded_value": """SENT_START keep in mind ( NNP how that the what when )""",
        "full_input": """Ad Hoc:
SENT_START keep in mind ( NNP how that the what when )
Rule Number:
30119
Correction:
Remember $4 @ Recall $4
Category:
Conciseness
Explanation:
Would using fewer words help tighten the sentence?
Test Sentence:
Keep in mind George Orwell’s six rules. 
Corrected Test Sentence:
Remember George Orwell’s six rules.

XML Rule:""",
        "expected_output": """<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30119">
    <pattern>
            <token postag="SENT_START"/>
            <marker>
                    <token>keep</token>
                    <token>in</token>
                    <token>mind</token>
                    <or>
                            <token postag="NNP"/>
                            <token regexp="yes">how|that|the|what|when</token>
                    </or>
            </marker>
    </pattern>
    <message>Would using fewer words help tighten the sentence?</message>
    <suggestion>Remember <match no="5"/></suggestion>
    <suggestion>Recall <match no="5"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":2,"priority":"5.128","WORD":true,"OUTLOOK":true}</short>
    <example correction="Remember George|Recall George"><marker>Keep in mind George</marker> Orwell`s six rules.</example>
</rule>"""
    },
    {
        "id": "ddced70f-c004-4218-b193-7bfb706b2ed6",
        "embedded_value": """( and is ) not without ( consequence consequences )""",
        "full_input": """Ad Hoc:
( and is ) not without ( consequence consequences )
Rule Number:
30120
Correction:
$0 significant @ $0 weighty @ $0 consequential 
Category:
Conciseness
Explanation:
Would using fewer words help tighten the sentence?
Test Sentence:
The event is not without consequence. 
Corrected Test Sentence:
The event is significant.

XML Rule:""",
        "expected_output": """<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30120">
        <pattern>
                <token regexp="yes">and|is</token>
                <token>not</token>
                <token>without</token>
                <token regexp="yes">consequence|consequences</token>
        </pattern>
        <message>Would using fewer words help tighten the sentence?</message>
        <suggestion><match no="1"/> significant</suggestion>
        <suggestion><match no="1"/> weighty</suggestion>
        <suggestion><match no="1"/> consequential</suggestion>
        <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":3,"priority":"4.145","WORD":true,"OUTLOOK":true}</short>
        <example correction="is significant|is weighty|is consequential">The event <marker>is not without consequence</marker>.</example>
</rule>"""
    },
    {
        "id": "ffefb4f3-6c1c-4958-96f2-96335ed1c75a",
        "embedded_value": """CT(be) ( fairly quite rather somewhat ) ( afraid available clear difficult easy essential good important likely necessary possible ready similar sure true wrong )""",
        "full_input": """Ad Hoc:
CT(be) ( fairly quite rather somewhat ) ( afraid available clear difficult easy essential good important likely necessary possible ready similar sure true wrong )
Rule Number:
30122
Correction:
$0 $2
Category:
Conciseness
Explanation:
Would cutting this implied modifier help strengthen the sentence?
Test Sentence:
It is quite easy to rewrite an article. 
Corrected Test Sentence:
It is easy to rewrite an article.

XML Rule:""",
        "expected_output": """<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30122">
    <pattern>
            <token inflected="yes">be</token>
            <token regexp="yes">fairly|quite|rather|somewhat</token>
            <token regexp="yes">afraid|available|clear|difficult|easy|essential|good|important|likely|necessary|possible|ready|similar|sure|true|wrong</token>
    </pattern>
    <message>Would cutting this implied modifier help strengthen the sentence?</message>
    <suggestion><match no="1"/> <match no="3"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"3.249","WORD":true,"OUTLOOK":true}</short>
    <example correction="is easy">It <marker>is quite easy</marker> to rewrite an article.</example>
</rule>"""
    },
    {
        "id": "'803b92ed-0909-4374-b71c-9618444f0dda'",
        "embedded_value": """really ( V.*? !did !do !have !know !think !want !wanted )""",
        "full_input": """Ad Hoc:
really ( V.*? !did !do !have !know !think !want !wanted )
Rule Number:
30123
Correction:
$1 
Category:
Conciseness
Explanation:
Would cutting this implied modifier help strengthen the sentence?
Test Sentence:
They may also wonder whether these two people really exist. 
Corrected Test Sentence:
They may also wonder whether these two people exist.

XML Rule:""",
        "expected_output": """<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30123">
    <pattern>
            <token>really</token>
            <token postag="V.*" postag_regexp="yes">
                    <exception regexp="yes">did|do|have|know|think|want|wanted</exception>
            </token>
    </pattern>
    <message>Would cutting this implied modifier help strengthen the sentence?</message>
    <suggestion><match no="2"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"2.159","WORD":true,"OUTLOOK":true}</short>
    <example correction="exist">They may also wonder whether these two people <marker>really exist</marker>.</example>
</rule>"""
    },
    {
        "id": "6bdd708d-7826-461f-8379-36efb6bd8602",
        "embedded_value": """(CT(be) and but they i he they have ) not ( generally typically usually ) ( RX(.*?) !accepted !considered !known )""",
        "full_input": """Ad Hoc:
(CT(be) and but they i he they have ) not ( generally typically usually ) ( RX(.*?) !accepted !considered !known )
Rule Number:
30124
Correction:
$0 rarely $3 @ $0 seldom $3 
Category:
Conciseness
Explanation:
Would using fewer words help tighten the sentence?
Test Sentence:
They are not generally definite articles.
Corrected Test Sentence:
They are rarely definite articles.

XML Rule:""",
        "expected_output": """<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30124">                                        
        <pattern>                                
                <or>                        
                        <token inflected="yes">be</token>                
                        <token regexp="yes">and|but|they|i|he|they|have</token>                
                </or>                        
                <token>not</token>                        
                <token regexp="yes">generally|typically|usually</token>                        
                <token>                        
                        <exception regexp="yes">accepted|considered|known</exception>                
                </token>                        
        </pattern>                                
        <message>Would using fewer words help tighten the sentence?</message>                                
        <suggestion><match no="1"/> rarely <match no="4"/></suggestion>                                
        <suggestion><match no="1"/> seldom <match no="4"/></suggestion>                                
        <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":2,"priority":"4.174","WORD":true,"OUTLOOK":true}</short>                                
        <example correction="are rarely definite|are seldom definite">They <marker>are not generally definite</marker> articles.</example>                                
</rule>"""
    },
    {
        "id": "f8f3905b-e658-48c8-aeee-850ddb330992",
        "embedded_value": """CT(do) not ( generally typically usually ) ( VB !give !include !take )""",
        "full_input": """Ad Hoc:
CT(do) not ( generally typically usually ) ( VB !give !include !take )
Rule Number:
30125
Correction:
rarely $3-$0 @ seldom $3-$0 
Category:
Conciseness
Explanation:
Would using fewer words help tighten the sentence?
Test Sentence:
They do not generally required a definite article.
Corrected Test Sentence:
They rarely require a definite article.

XML Rule:""",
        "expected_output": """<rule id="{new_rule_id}" name="BRIEFCATCH_CONCISENESS_30125">
    <pattern>
        <marker>
            <token inflected="yes">do</token>
            <token>not</token>
            <token regexp="yes">generally|typically|usually</token>
            <token postag="VB" postag_regexp="yes">
                <exception regexp="yes">give|include|take</exception>
            </token>
        </marker>
    </pattern>
    <message>Would using fewer words help tighten the sentence?</message>
    <suggestion>rarely <match no="4"/></suggestion>
    <suggestion>seldom <match no="4"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":2,"priority":"5.262","WORD":true,"OUTLOOK":true}</short>
    <example correction="They rarely require|They seldom require">They <marker>do not generally require</marker> a definite article.</example>
</rule>"""
    },
    {
        "id": "c9ddd990-ec19-4eb5-973e-8e32ab9188cd",
        "embedded_value": """( RX(.*?) !closed !him !prohibited !time !times !used ) except when ( he i it otherwise the there they we you )""",
        "full_input": """Ad Hoc:
( RX(.*?) !closed !him !prohibited !time !times !used ) except when ( he i it otherwise the there they we you )
Rule Number:
30132
Correction:
$0 unless $3
Category:
Fresh Language
Explanation:
Would direct language such as <i>unless</i> convey your point just as effectively?<linebreak/><linebreak/><b>Example</b> from Justice Sotomayor: “[I]t contends that no aged-out child may retain her priority date <b>unless</b> her petition is also eligible for automatic conversion.”<linebreak/><linebreak/><b>Example</b> from Office of Legal Counsel: “The 2019 Opinion reasoned that Congress lacks constitutional authority to compel the Executive Branch . . . even when a statute vests the committee with a right to the information, <b>unless</b> the information would serve a legitimate legislative purpose.”<linebreak/><linebreak/><b>Example</b> from Morgan Chu: “During this arbitration, [Defendant] stopped paying royalties and refused to pay anything <b>unless</b> ordered to do so.”<linebreak/><linebreak/><b>Example</b> from Paul Clement: “The bottom line is that there is no preemption <b>unless</b> state law conflicts with some identifiable federal statute.”<linebreak/><linebreak/><b>Example</b> from Andy Pincus: “The law does not permit a claim for defamation <b>unless</b> the allegedly false statement has caused actual harm.”<linebreak/><linebreak/><b>Example</b> from Microsoft’s Standard Contract: “Licenses granted on a subscription basis expire at the end of the applicable subscription period set forth in the Order, <b>unless</b> renewed.”
Test Sentence:
Omit except when it is part of a name.
Corrected Test Sentence:
Omit unless it is part of a name.

XML Rule:""",
        "expected_output": """<rule id="{new_rule_id}" name="BRIEFCATCH_DIRECT_LANGUAGE_30132">
        <pattern>
                <token>
                        <exception regexp="yes">closed|him|prohibited|time|times|used</exception>
                </token>
                <token>except</token>
                <token>when</token>
                <token regexp="yes">he|i|it|otherwise|the|there|they|we|you</token>
        </pattern>
        <message>Would direct language such as *unless* convey your point just as effectively?|**Example** from Justice Sotomayor: “[I]t contends that no aged-out child may retain her priority date **unless** her petition is also eligible for automatic conversion.”|**Example** from Office of Legal Counsel: “The 2019 Opinion reasoned that Congress lacks constitutional authority to compel the Executive Branch . . . even when a statute vests the committee with a right to the information, **unless** the information would serve a legitimate legislative purpose.”|**Example** from Morgan Chu: “During this arbitration, [Defendant] stopped paying royalties and refused to pay anything **unless** ordered to do so.”|**Example** from Paul Clement: “The bottom line is that there is no preemption **unless** state law conflicts with some identifiable federal statute.”|**Example** from Andy Pincus: “The law does not permit a claim for defamation **unless** the allegedly false statement has caused actual harm.”|**Example** from Microsoft's Standard Contract: “Licenses granted on a subscription basis expire at the end of the applicable subscription period set forth in the Order, **unless** renewed.”</message>
        <suggestion><match no="1"/> unless <match no="4"/></suggestion>
        <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"4.225","WORD":true,"OUTLOOK":true}</short>
        <example correction="Omit unless it"><marker>Omit except when it</marker> is part of a name.</example>
</rule>"""
    },
    {
        "id": "8a8e368b-fd2d-4caa-8016-4eea694b6216",
        "embedded_value": """SENT_START in that case , ( however though ) , ( i he if in it she there this )""",
        "full_input": """Ad Hoc:
SENT_START in that case , ( however though ) , ( i he if in it she there this )
Rule Number:
30136
Correction:
But $7 @ Then $6 $7 @ But then $7
Category:
Flow
Explanation:
Could shortening your opening transition add punch and help lighten the style?<linebreak/><linebreak/><b>Example</b> from Chief Justice Roberts: “<b>But</b> that argument . . . confuses mootness with the merits.”
Test Sentence:
In that case, however, this subtitle should tell you.
Corrected Test Sentence:
But this subtitle should tell you.

XML Rule:""",
        "expected_output": """<rule id="{new_rule_id}" name="BRIEFCATCH_FLOW_30136">
    <pattern>
            <token postag="SENT_START"/>
            <marker>
                    <token>in</token>
                    <token>that</token>
                    <token>case</token>
                    <token>,</token>
                    <token regexp="yes">however|though</token>
                    <token>,</token>
                    <token regexp="yes">he|i|if|in|it|she|there|this</token>
            </marker>
    </pattern>
    <message>Could shortening your opening transition add punch and help lighten the style?|**Example** from Chief Justice Roberts: “**But** that argument . . . confuses mootness with the merits.”</message>
    <suggestion>But <match no="8"/></suggestion>
    <suggestion>Then<match no="7"/> <match no="8"/></suggestion>
    <suggestion>But then <match no="8"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":3,"priority":"8.252","WORD":true,"OUTLOOK":true}</short>
    <example correction="But this|Then, this|But then this"><marker>In that case, however, this</marker> subtitle should tell you.</example>
</rule>"""
    },
    {
        "id": "78f28891-9e4f-4779-972a-7776cdce13dd",
        "embedded_value": """( RX(.*?) !for !in !on !that !through !to !with ) the use of the ( RX(.*?) !band !land !phrase !verb !word !words )""",
        "full_input": """Ad Hoc:
( RX(.*?) !for !in !on !that !through !to !with ) the use of the ( RX(.*?) !band !land !phrase !verb !word !words )
Rule Number:
30156
Correction:
$0 using $4 $5
Category:
Conciseness
Explanation:
Would using fewer words and cutting the <i>of</i> phrase help tighten the sentence?
Test Sentence:
But the use of the dictionary is wrong.
Corrected Test Sentence:
But using the dictionary is wrong.

XML Rule:""",
        "expected_output": """<rule id="{new_rule_id}" name="BRIEFCATCH_PUNCHINESS_30156">
    <pattern>
            <token>
                    <exception regexp="yes">for|in|on|that|through|to|with</exception>
            </token>
            <token>the</token>
            <token>use</token>
            <token>of</token>
            <token>the</token>
            <token>
                    <exception regexp="yes">band|land|phrase|verb|word|words</exception>
            </token>
    </pattern>
    <message>Would using fewer words and cutting the *of* phrase help tighten the sentence?</message>
    <suggestion><match no="1"/> using <match no="5"/> <match no="6"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"6.286","WORD":true,"OUTLOOK":true}</short>
    <example correction="But using the dictionary"><marker>But the use of the dictionary</marker> is wrong.</example>
</rule>"""
    },
    {
        "id": "2ad2b349-5ed1-404a-a8fe-0738cd21f97d",
        "embedded_value": """( CT(be) and ) a bit ( JJ.*? more !much !of )""",
        "full_input": """Ad Hoc:
( CT(be) and ) a bit ( JJ.*? more !much !of )
Rule Number:
30115
Correction:
$0 $3
Category:
Conciseness
Explanation:
Would cutting <i>a bit</i> help tighten the sentence?
Test Sentence:
The book does this and a bit more. 
Corrected Test Sentence:
The book does this and more. 

XML Rule:""",
        "expected_output": """<rule id="BRIEFCATCH_164054315699492609263729987293589324728" name="BRIEFCATCH_CONCISENESS_30115">
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
        <message>Would cutting *a bit* help tighten the sentence?</message>
        <suggestion><match no="1"/> <match no="4"/></suggestion>
        <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":1,"priority":"4.174","WORD":true,"OUTLOOK":true}</short>
        <example correction="and more.">The book does this <marker>and a bit more</marker>.</example>
</rule>"""
    },
    {
        "id": "2348ea87-a1ca-4c05-b50a-13c32d098779",
        "embedded_value": """a ( sudden ~ ) surprise move""",
        "full_input": """Ad Hoc:
a ( sudden ~ ) surprise move
Rule Number:
3240
Correction:
a surprise @ a move @ surprising @ unexpected
Category:
Fresh Language
Explanation:
<b>A surprise move</b> is a cliché. Could direct language convey your point just as effectively?
Test Sentence:
She made a sudden surprise move. 
Corrected Test Sentence:
She made a surprise.

XML Rule:""",
        "expected_output": """<rule id="BRIEFCATCH_4496626169111403644393793089759868674587" name="BRIEFCATCH_FRESH_LANGUAGE_3240">
    <pattern>
        <token>a</token>
        <token min="0">sudden</token>
        <token>surprise</token>
        <token>move</token>
    </pattern>
    <message>*A surprise move* is a cliché. Could direct language convey your point just as effectively?</message>
    <suggestion>a surprise</suggestion>
    <suggestion>a move</suggestion>
    <suggestion>surprising</suggestion>
    <suggestion>unexpected</suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":4,"priority":"5.0","WORD":true,"OUTLOOK":true}</short>
    <example correction="a surprise|a move|surprising|unexpected">She made <marker>a sudden surprise move</marker>.</example>
</rule>"""
    },
    {
        "id": "f252ffd3-07a4-4064-acba-ea7f04473c45",
        "embedded_value": """CT(do) not ( generally typically usually ) ( VB !give !include !take )""",
        "full_input": """Ad Hoc:
CT(do) not ( generally typically usually ) ( VB !give !include !take )
Rule Number:
30125
Correction:
rarely $3-$0 @ seldom $3-$0
Category:
Conciseness
Explanation:
Would using fewer words help tighten the sentence?
Test Sentence:
They do not generally required a definite article.
Corrected Test Sentence:
They rarely require a definite article.

XML Rule:""",
        "expected_output": """<rule id="BRIEFCATCH_263762808715424542820983160320978225970" name="BRIEFCATCH_CONCISENESS_30125">                                        
        <pattern>                                
            <token inflected="yes">do</token>                        
            <token>not</token>                        
            <token regexp="yes">generally|typically|usually</token>                        
            <token postag="VB">                        
                <exception regexp="yes">give|include|take</exception>                
            </token>                        
        </pattern>
        <filter class="org.languagetool.rules.en.AdvancedSynthesizerFilter" args="lemmaFrom:4 lemmaSelect:V.* postagFrom:1 postagSelect:V.*"/>                                
        <message>Would using fewer words help tighten the sentence?</message>                                
        <suggestion>rarely {suggestion}</suggestion>                                
        <suggestion>seldom {suggestion}</suggestion>                                
        <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":2,"priority":"4.174","WORD":true,"OUTLOOK":true}</short>                                
        <example correction="rarely require|seldom require">They <marker>do not generally require</marker> a definite article.</example>                                
</rule>"""
    },
    {
        "id": "864a6eef-900a-48c4-b89a-163ecc2ee589",
        "embedded_value": """SENT_START in that case , ( however though ) , ( i he if in it she there this )""",
        "full_input": """Ad Hoc:
SENT_START in that case , ( however though ) , ( i he if in it she there this )
Rule Number:
30136
Correction:
But $7 @ Then $6 $7 @ But then $7
Category:
Flow
Explanation:
Could shortening your opening transition add punch and help lighten the style?<linebreak/><linebreak/><b>Example</b> from Chief Justice Roberts: “<b>But</b> that argument . . . confuses mootness with the merits.”
Test Sentence:
In that case, however, this subtitle should tell you.
Corrected Test Sentence:
But this subtitle should tell you.

XML Rule:""",
        "expected_output": """<rule id="BRIEFCATCH_145346392105646606287940325719406917958" name="BRIEFCATCH_FLOW_30136">
    <pattern>
        <token postag="SENT_START"/>
        <marker>
            <token>in</token>
            <token>that</token>
            <token>case</token>
            <token>,</token>
            <token regexp="yes">however|though</token>
            <token>,</token>
            <token regexp="yes">he|i|if|in|it|she|there|this</token>
        </marker>
    </pattern>
    <message>Could shortening your opening transition add punch and help lighten the style?|**Example** from Chief Justice Roberts: “**But** that argument . . . confuses mootness with the merits.”</message>
    <suggestion>But <match no="8"/></suggestion>
    <suggestion>Then<match no="7"/> <match no="8"/></suggestion>
    <suggestion>But then <match no="8"/></suggestion>
    <short>{"ruleGroup":null,"ruleGroupIdx":0,"isConsistency":false,"isStyle":true,"correctionCount":3,"priority":"8.252","WORD":true,"OUTLOOK":true}</short>
    <example correction="But this|Then, this|But then this"><marker>In that case, however, this</marker> subtitle should tell you.</example>
</rule>"""
    }
]


# {
#     "embedded_value": """""",
#     "full_input": """""",
#     "expected_output": """"""
# }


insert_into_pinecone(index_name=os.getenv("PINECONE_INDEX"), namespace="adhoc-rule-creation", records=data)
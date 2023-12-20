from pydantic import BaseModel
from typing import List, Optional


class InputData(BaseModel):
    input_text: str


class InputDataList(BaseModel):
    input_texts: List[str]


class SentenceRankingInputRow(BaseModel):
    sentence_number: str
    rule_number: str
    text: str
    corrected_text: str


class SentenceRankingInput(BaseModel):
    input_data: List[SentenceRankingInputRow]


class RuleInputData(BaseModel):
    target_element: str
    element_action: str
    specific_actions: List[str]
    original_rule_text: Optional[str] = None


class UpdateRuleInput(BaseModel):
    modified_rule_name: str
    modified_rule: str


class CreateRuleInput(BaseModel):
    ad_hoc_syntax: str
    rule_number: str
    correction: str
    category: str
    explanation: str
    test_sentence: str
    test_sentence_correction: str


class NgramInput(BaseModel):
    rule_pattern: str
    suggestion_pattern: Optional[str] = None
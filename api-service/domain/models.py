from pydantic import BaseModel
from typing import List, Optional
from domain.constants import Modifications


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
    selected_modification: Modifications
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
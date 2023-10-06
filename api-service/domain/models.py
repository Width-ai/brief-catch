from pydantic import BaseModel
from typing import List, Optional
from domain.constants import Actions


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
    action_to_take: Actions
    specific_actions: List[str]
    original_rule_text: Optional[str] = None
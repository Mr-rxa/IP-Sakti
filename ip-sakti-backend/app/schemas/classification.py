from pydantic import BaseModel, Field
from typing import List, Optional, Union

class ClassificationStartRequest(BaseModel):
    session_id: str

class ClassificationAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str

class ClassificationQuestionResponse(BaseModel):
    question_id: Optional[str] = None
    next_question_id: Optional[str] = None
    question_text: str
    options: Optional[List[str]] = None

class ClassificationFinalResultResponse(BaseModel):
    classification_result: str
    explanation: str
    relevant_regimes: List[str]
    required_ip_checks: Optional[List[str]] = None
    required_regulatory_checks: Optional[List[str]] = None

ClassificationResponse = Union[ClassificationQuestionResponse, ClassificationFinalResultResponse]

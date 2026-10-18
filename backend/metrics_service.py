"""Read actual evaluation reports; placeholders and corrupt files are unavailable."""

import json
import math
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError, field_validator

Score = Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)]
Count = Annotated[int, Field(strict=True, ge=0)]


class EvaluationReport(BaseModel):
    model_config = ConfigDict(extra='allow')

    available: Literal[True]
    model: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    split: Literal['test']
    accuracy: Score
    precision_macro: Score
    recall_macro: Score
    f1_macro: Score
    confusion_matrix: list[list[Count]]

    @field_validator('confusion_matrix')
    @classmethod
    def square_matrix(cls, value):
        if not value or any(len(row) != len(value) for row in value):
            raise ValueError('confusion_matrix must be nonempty and square')
        return value


def reject_nonfinite(value):
    raise ValueError(f'Nonfinite JSON number: {value}')


def finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('JSON number exceeds finite floating-point range')
    return number


def read_report(path: Path) -> dict:
    if not path.is_file():
        return {'available': False, 'reason': 'Chưa có báo cáo đánh giá thực nghiệm.'}
    try:
        report = json.loads(path.read_text(encoding='utf-8'), parse_constant=reject_nonfinite,
                            parse_float=finite_float)
        if isinstance(report, dict) and report.get('available') is False:
            return {'available': False, 'reason': str(report.get('reason', 'Chưa đánh giá mô hình.'))}
        return EvaluationReport.model_validate(report).model_dump()
    except (OSError, UnicodeError, ValueError, ValidationError):
        return {'available': False, 'error': 'Báo cáo ML không hợp lệ; kiểm tra schema trong API_CONTRACT.md.'}

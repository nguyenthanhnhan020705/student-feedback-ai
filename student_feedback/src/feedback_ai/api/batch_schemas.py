from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Literal
class Row(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    id: StrictStr=Field(max_length=100)
    source_row: int=Field(ge=1)
    text: StrictStr=Field(max_length=20000)
    status: Literal['ok','error','invalid','pending']
    sentiment: Literal['positive','negative','mixed','undetermined'] | None=None
    topics: list[Literal['lecturer','curriculum','facility']]=Field(default_factory=list,max_length=3)
    aspects: dict[Literal['lecturer','curriculum','facility'],Literal['positive','negative','mixed','undetermined']]=Field(default_factory=dict)
    error: StrictStr=Field(default='',max_length=500)
class ExportRequest(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    name: StrictStr=Field(default='',max_length=200)
    rows: list[Row]=Field(min_length=1,max_length=500)

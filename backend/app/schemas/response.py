from pydantic import BaseModel
from typing import List

class ImageAnalysisResponse(BaseModel):
    caption: str
    summary: str
    objects: List[str]
    emotion: str
    story: str

from pydantic import BaseModel
from typing import List

class SourceConfig(BaseModel):
    type: str
    params: dict

class TransformConfig(BaseModel):
    name: str
    params: dict

class LoadConfig(BaseModel):
    type: str
    params: dict

class VizConfig(BaseModel):
    type: str
    params: dict

class PipelineSpec(BaseModel):
    sources: List[SourceConfig]
    transforms: List[TransformConfig]
    load: LoadConfig
    viz: VizConfig

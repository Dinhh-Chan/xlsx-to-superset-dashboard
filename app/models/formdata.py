from pydantic import BaseModel, Field, validator  
from typing import List, Optional 
import json 
class FormDataRequests(BaseModel):
    id_chart: int = Field(...,example =645)
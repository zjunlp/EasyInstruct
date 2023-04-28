import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

import yaml
from pydantic import Extra, Field, validator,BaseModel

class BaseEngine(BaseModel, ABC):

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @abstractmethod
    def _call(self, prompt: str, stop: Optional[List[str]] = None,**kwargs) -> str:
        """Run the LLM on the given prompt and input."""
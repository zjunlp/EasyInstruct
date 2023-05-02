from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import Extra, BaseModel

class BaseEngine(BaseModel, ABC):

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @abstractmethod
    def _call(self, prompt: str, stop: Optional[List[str]] = None,**kwargs) -> str:
        """Run the LLM on the given prompt and input."""
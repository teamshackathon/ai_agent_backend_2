from pydantic import BaseModel


class BaseInput(BaseModel):
    """Base input schema for all chains"""

    pass


class BaseOutput(BaseModel):
    """Base output schema for all chains"""

    pass

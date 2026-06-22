from typing import Final
from pydantic import BaseModel


class OpenRPCModel(BaseModel):
    """Base model for OpenRPC documents."""

    pass


OPENRPC_VERSION: Final = "1.3.2"

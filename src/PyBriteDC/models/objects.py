import enum
from typing import List
from typing import Union

from pydantic import BaseModel


class SatelliteEnum(enum.Enum):
    BAb = "BAb"
    UBr = "UBr"
    BTr = "BTr"
    BLb = "BLb"
    BHr = "BHr"


class Field(BaseModel):
    field_number: int


class Star(BaseModel):
    hd_number: int


class SingleObservation(BaseModel):
    satellite: SatelliteEnum
    setup: Union[int, List[int]]

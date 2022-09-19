from typing import List

import numpy as np
from pydantic import BaseModel

from PyBriteDC.models import file as mf
from PyBriteDC.models import objects as mo


class MergedSingleObservationRaw(mo.SingleObservation):
    ndat_data: np.ndarray  # type: ignore
    ave_data: np.ndarray  # type: ignore
    orig_data: np.ndarray  # type: ignore

    class Config:
        arbitrary_types_allowed = True


class MergedSingleObservation(mo.SingleObservation):
    ndat_file: str
    ave_file: str
    orig_file: str

    ndat_datapoints: int
    orig_datapoints: int

    rms: float
    ptp_scatter: float
    noise: float
    rms_per_orbit: float


class MergedStar(mo.Star):
    path: str
    single_observations: List[MergedSingleObservation]
    spectral_type: str
    b_magnitude: float
    v_magnitude: float
    abs_magnitude: float
    parallax: float
    distance: float


class MergedField(mo.Field):
    path: str
    stars: List[MergedStar]


class MergedModel(BaseModel):
    path: str
    fields: List[MergedField]

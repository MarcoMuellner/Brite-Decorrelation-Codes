from typing import List, Optional

from pydantic import BaseModel
from PyBriteDC.models import objects as mo


class FileSystemSingleObservation(mo.SingleObservation):
    orig_files: List[str]
    ndat_files: List[str]
    ave_files: Optional[List[str]]
    combined_data: Optional[bool] = False


class FileSystemStar(mo.Star):
    path: str
    single_observations: List[FileSystemSingleObservation]


class FileSystemField(mo.Field):
    path: str
    stars: List[FileSystemStar]


class FileSystemModel(BaseModel):
    path: str
    fields: List[FileSystemField]

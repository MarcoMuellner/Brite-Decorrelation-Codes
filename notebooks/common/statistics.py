from typing import List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .brite_paths import Data, load, Star


class IStatPointObject:
    def get_name(self):
        raise NotImplementedError("Get Name needs to be implemented!")

    def get_datapoint(self, data: Data):
        raise NotImplementedError("Get DataPoint needs to be implemented!")


def getStatPointObjects() -> List[IStatPointObject]:
    return [

    ]


class AnalyzeStar:
    STAR_NAME = "Starname"
    STAR_FIELD = "Field"
    STAR_SETUP = "Setup"
    SATELLITE = "Satellite"

    def __init__(self, field: int):
        self._stars = load(field)

    def load_data(self):
        self._data_dict = {}
        self._data_list = []
        for star in self._stars:
            for star_results in star.results:
                self._data_list += star.get_all_data(star_results)

        self._data_dict[self.STAR_NAME] = []
        self._data_dict[self.STAR_FIELD] = []
        self._data_dict[self.STAR_SETUP] = []
        self._data_dict[self.SATELLITE] = []

        for statPoint in getStatPointObjects():
            if not issubclass(statPoint.__class__, IStatPointObject):
                raise Exception(
                    "StatPointObject needs to implement IStatPointObject --> " + statPoint.__class__.__name__)
            self._data_dict[statPoint.get_name()] = []

    def process_stars(self) -> pd.DataFrame:
        for data in self._data_list:
            self._data_dict[self.STAR_NAME].append(data.starname)
            self._data_dict[self.STAR_FIELD].append(data.field)
            self._data_dict[self.STAR_SETUP].append(data.setup)
            self._data_dict[self.SATELLITE].append(data.satellite)
            for statPoint in getStatPointObjects():
                self._data_dict[statPoint.get_name()].append(statPoint.get_datapoint(data))

        return pd.DataFrame.from_dict(self._data_dict)

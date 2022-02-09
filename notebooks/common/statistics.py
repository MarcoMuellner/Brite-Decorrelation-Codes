from typing import List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

from .brite_paths import Data, load, Star


class IStatPointObject:
    def get_name(self) -> str:
        raise NotImplementedError("Get Name needs to be implemented!")

    def get_datapoint(self, data: Data) -> float:
        raise NotImplementedError("Get DataPoint needs to be implemented!")


class SpectraTypeStat(IStatPointObject):
    def get_name(self) -> str:
        return f"Spectral Type"

    def get_datapoint(self, data: Data) -> float:
        try:
            return data.star.simbad["SP_TYPE"].value.data[0][0]
        except Exception as e:
            raise e


class VMagnitudeStat(IStatPointObject):
    def get_name(self) -> str:
        return f"V Magnitude"

    def get_datapoint(self, data: Data) -> float:
        try:
            return data.star.simbad['FLUX_V'].value.data[0]
        except Exception as e:
            raise e


class RMSPerOrbit(IStatPointObject):
    def get_name(self) -> str:
        return f"RMS per orbit"

    def get_datapoint(self, data: Data) -> float:
        ave_data = data.get_averaged_lightcurve(True)
        return np.sqrt(np.sum(ave_data.flux.value ** 2) / len(ave_data.flux))


def getStatPointObjects() -> List[IStatPointObject]:
    return [
        VMagnitudeStat(),
        SpectraTypeStat(),
        RMSPerOrbit()
    ]


class AnalyzeStar:
    STAR_NAME = "Starname"
    STAR_FIELD = "Field"
    STAR_SETUP = "Setup"
    SATELLITE = "Satellite"
    MERGED = "Merged"
    FILEPATH = "Filepath"

    def __init__(self, field: int):
        self._stars = load(field)

    def load_data(self):
        self._data_dict = {}
        self._data_list = []
        for star in tqdm(self._stars):
            for star_results in star.results:
                self._data_list += star.get_all_data(star_results)

        self._data_dict[self.STAR_NAME] = []
        self._data_dict[self.STAR_FIELD] = []
        self._data_dict[self.STAR_SETUP] = []
        self._data_dict[self.SATELLITE] = []
        self._data_dict[self.MERGED] = []
        self._data_dict[self.FILEPATH] = []

        for statPoint in getStatPointObjects():
            if not issubclass(statPoint.__class__, IStatPointObject):
                raise Exception(
                    "StatPointObject needs to implement IStatPointObject --> " + statPoint.__class__.__name__)
            self._data_dict[statPoint.get_name()] = []

    def process_stars(self) -> pd.DataFrame:
        for data in tqdm(self._data_list):
            data: Data
            self._data_dict[self.STAR_NAME].append(data.starname)
            self._data_dict[self.STAR_FIELD].append(data.field)
            self._data_dict[self.STAR_SETUP].append(data.setup)
            self._data_dict[self.SATELLITE].append(data.satellite)
            self._data_dict[self.MERGED].append(data.combined)
            self._data_dict[self.FILEPATH].append(data.path)
            for statPoint in getStatPointObjects():
                try:
                    self._data_dict[statPoint.get_name()].append(statPoint.get_datapoint(data))
                except Exception as e:
                    print(
                        f"{statPoint.get_name()} failed with {e} for {data.starname} {data.setup} {data.field} {data.satellite}")
                    self._data_dict[statPoint.get_name()].append(None)

        return pd.DataFrame.from_dict(self._data_dict)

import itertools
import os
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np

from PyBriteDC.models import file as mf
from PyBriteDC.models import observation as mo


def combine_file_data(
    files: List[str], normalizer_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None
) -> Optional[np.ndarray]:
    """
    Combines a given list of files into a numpy array.
    :param normalizer_fn: An optional normalizer function, applied to the loaded array directly after loading.
    :param files: Files to combine.
    :return: numpy array of combined files.
    """
    data = None
    for file in files:
        local_data = np.loadtxt(file)

        if normalizer_fn is not None:
            local_data = normalizer_fn(local_data)

        if data is None:
            data = local_data
        else:
            data = np.concatenate((data, local_data), axis=0)
    return data


def combine_observations(
    star: mf.FileSystemStar,
) -> List[mo.MergedSingleObservationRaw]:
    """
    Combines all observations from a given FileSystemStar object (ndat, ave and orig2) and
    generates the combined datasets.
    :param star : The FileSystemStar object to combine.
    :return: A list of MergedSingleObservationRaw objects for any given star object.
    """

    data = []

    for satellite in list({i.satellite for i in star.single_observations}):
        # get list of all ndat files and flatten it into one list
        orig_files = list(
            itertools.chain(
                *[
                    [j for j in i.orig_files]
                    for i in star.single_observations
                    if i.satellite == satellite
                ]
            )
        )
        ndat_files = list(
            itertools.chain(
                *[
                    [j for j in i.ndat_files]
                    for i in star.single_observations
                    if i.satellite == satellite
                ]
            )
        )
        ave_files = list(
            itertools.chain(
                *[
                    [j for j in i.ave_files]
                    for i in star.single_observations
                    if i.satellite == satellite and i.ave_files is not None
                ]
            )
        )

        def remove_median(data: np.ndarray) -> np.ndarray:
            data[:, 1] = data[:, 1] - np.median(data[:, 1])
            return data

        # combine all ndat files into one numpy array
        ndat_data = combine_file_data(ndat_files, remove_median)
        ave_data = combine_file_data(ave_files, remove_median)
        orig_data = combine_file_data(orig_files)

        if any(
            [
                isinstance(i.setup, list)
                for i in star.single_observations
                if i.satellite == satellite
            ]
        ):
            raise ValueError("Multiple setups not yet supported in combinations.")

        data.append(
            mo.MergedSingleObservationRaw(
                satellite=satellite,
                setup=[
                    i.setup
                    for i in star.single_observations
                    if i.satellite == satellite
                ],
                orig_data=orig_data,
                ndat_data=ndat_data,
                ave_data=ave_data,
            )
        )

    return data

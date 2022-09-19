import itertools
import os
import re
from typing import List
from typing import Optional

from PyBriteDC.common import regular_expressions as regex
from PyBriteDC.models import file as mf
from PyBriteDC.models import objects as ob


def find_data(path: str) -> mf.FileSystemModel:
    """
    Parses a given file path to search for reduced Brite Observations.
    :param path: The path to parse.
    :return: A FileSystemModel object.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist.")

    fields: List[mf.FileSystemField] = [
        find_stars(os.path.join(path, i))
        for i in os.listdir(path)
        if "field" in i.lower() and os.path.isdir(os.path.join(path, i))
    ]

    return mf.FileSystemModel(path=path, fields=fields)


def find_stars(path: str) -> mf.FileSystemField:
    """
    Parses a given file path to search for reduced Brite Observations.
    :param path: The path to parse.
    :return: A FileSystemField object.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist.")

    stars: List[mf.FileSystemStar] = list(
        itertools.chain(
            *[
                [
                    find_observations(os.path.join(root, i))
                    for i in dirs
                    if os.path.isdir(os.path.join(root, i))
                    and regex.hd_descriptor.search(i) is not None
                ]
                for root, dirs, found_files in os.walk(path)
            ]
        )
    )

    field_number = regex.field_descriptor.search(path)

    return mf.FileSystemField(path=path, stars=stars, field_number=int(field_number.group("field_number")))  # type: ignore


def check_if_file_valid_for_process(file_name: str, hd_number: int) -> bool:
    file_name_check = (
        regex.file_descriptor.search(file_name) is not None
        and f"{hd_number}" in file_name
    )
    merged_check = "merged" not in file_name
    return file_name_check and merged_check


def find_observations(path: str) -> mf.FileSystemStar:
    """
    Parses a given file path to search for reduced Brite Observations.
    :param path: The path to parse.
    :return: A FileSystemSingleObservation object.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist.")

    hd_number_match = regex.hd_descriptor.search(path)

    if hd_number_match is None:
        raise ValueError(f"{path} doesn't contain a HD number!")

    hd_number: int = int(hd_number_match.group(1))

    files = []
    for root, dirs, found_files in os.walk(path):
        files += [
            os.path.join(root, i)
            for i in found_files
            if check_if_file_valid_for_process(i, hd_number)
        ]

    # Returns the list of satellites available for this set of observations
    available_satellites = list({regex.file_descriptor.search(i).group("satellite") for i in files})  # type: ignore

    observations: List[mf.FileSystemSingleObservation] = []

    def has_parts(files: List[str]) -> bool:
        return len([i for i in files if re.search(r"_part\d+", i) is not None]) == len(
            files
        )

    for satellite in available_satellites:
        matching_files = [i for i in files if satellite in i]
        available_setups = [regex.file_descriptor.search(i).group("setup") for i in matching_files]  # type: ignore
        for setup in list(set(available_setups)):
            orig_files = [
                i for i in matching_files if i.endswith(".orig2") and setup in i
            ]
            ndat_files = [
                i for i in matching_files if i.endswith(".ndat") and setup in i
            ]
            ave_files: Optional[List[str]] = [
                i for i in matching_files if i.endswith(".ave") and setup in i
            ]

            if len(orig_files) != 1 and not has_parts(orig_files):
                raise ValueError(
                    f"{path}, {satellite}, {setup} has {len(orig_files)} orig files."
                )

            if len(ndat_files) != 1 and not has_parts(ndat_files):
                raise ValueError(
                    f"{path}, {satellite}, {setup} has {len(ndat_files)} ndat files."
                )

            if ave_files is None or len(ave_files) != 1 and not has_parts(ave_files):
                print(
                    f"Warning: {path}, {satellite}, {setup} has {len(ave_files) if ave_files is not None else None} ave files."
                )
                ave_files = None
            else:
                ave_files = ave_files

            file_single_obs = mf.FileSystemSingleObservation(
                orig_files=orig_files,
                ndat_files=ndat_files,
                ave_files=ave_files,
                satellite=ob.SatelliteEnum(satellite),
                setup=int(setup.split("_")[0]),
            )
            observations += [file_single_obs]

    return mf.FileSystemStar(
        path=path, single_observations=observations, hd_number=hd_number
    )

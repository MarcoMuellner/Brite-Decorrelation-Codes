import os

import pytest

from PyBriteDC.models import file as mf
from PyBriteDC.models import objects as ob
from PyBriteDC.prep import combiner as cb
from PyBriteDC.prep import filesystem as fs


test_data_with_content = os.path.join(os.path.dirname(__file__), "testdata")
test_data_decor_path_bad = os.path.join(
    os.path.dirname(__file__), "testdata", "decorrelations_structure_bad"
)
test_data_decor_path_good = os.path.join(
    os.path.dirname(__file__), "testdata", "decorrelations_structure_good"
)


def test_find_fields():
    data = fs.find_data(test_data_decor_path_good)
    assert len(data.fields) == 17


@pytest.mark.parametrize(
    "file_name, hd_number, expected",
    [
        ("HD31237_01-Ori-I-2013_BAb_3.freq0", 31237, False),
        ("HD31237_01-Ori-I-2013_BAb_3_2_A.ave", 31237, True),
        ("HD31237_01-Ori-I-2013_BAb_3_2_A.ndat", 31237, True),
        ("HD31237_01-Ori-I-2013_BAb_3_2_A.orig2", 31237, True),
        ("HD31237_01-Ori-I-2013_BAb_3.freq0", 44743, False),
        ("HD31237_01-Ori-I-2013_BAb_3_2_A.ave", 44743, False),
        ("HD31237_01-Ori-I-2013_BAb_3_2_A.ndat", 44743, False),
        ("HD31237_01-Ori-I-2013_BAb_3_2_A.orig2", 44743, False),
        ("HD31237_01-Ori-I-2013_BAb_4_3_2_merged_.ave", 31237, False),
        ("HD31237_01-Ori-I-2013_BAb_4_3_2_merged_.ndat", 31237, False),
        ("HD44743_12-CMaPup-I-2015_BTr_1-2-3_4_A.ndat", 44743, False),
        ("HD44743_12-CMaPup-I-2015_BLb_4_5_5_4.ave", 44743, False),
        ("HD142669_09-Sco-I-2015_BLb_1-2-3-4-5-6_3_A.ndat", 142669, False),
        (
            "HD138690_09-Sco-I-2015_BLb_['4']_['5']_['3']_['2']_['6']_['1']_3_merged_.ndat",
            138690,
            False,
        ),
    ],
)
def test_is_valid_file(file_name, hd_number, expected):
    assert fs.check_if_file_valid_for_process(file_name, hd_number) == expected


@pytest.mark.parametrize(
    "path, expected",
    [
        (
            os.path.join(
                test_data_decor_path_bad, "Field 1 - Ori I (Andrzej)", "HD31237"
            ),
            3,
        ),
        (
            os.path.join(
                test_data_decor_path_bad, "Field 1 - Ori I (Andrzej)", "HD37043"
            ),
            3,
        ),
        (os.path.join(test_data_decor_path_bad, "Field 12", "HD_44743"), 5),
        (os.path.join(test_data_decor_path_bad, "Field 9", "HD_139365"), None),
    ],
)
def test_find_observations(path: str, expected: int):
    if expected is None:
        with pytest.raises(ValueError):
            fs.find_observations(path)
    else:
        star_observation = fs.find_observations(path)
        assert len(star_observation.single_observations) == expected
        for i in star_observation.single_observations:
            assert isinstance(i, mf.FileSystemSingleObservation)


@pytest.mark.parametrize(
    "path, expected",
    [
        (os.path.join(test_data_decor_path_bad, "Field 1 - Ori I (Andrzej)"), 15),
        (os.path.join(test_data_with_content, "Field_1_with_content"), 15),
        (os.path.join(test_data_decor_path_bad, "Field 2 - Cen I (Andrzej)"), 32),
        (os.path.join(test_data_decor_path_bad, "Field 3 - Sgr I (Andrzej)"), 19),
        (os.path.join(test_data_decor_path_bad, "Field 4 - Cyg I (Andrzej)"), 36),
        (os.path.join(test_data_decor_path_bad, "Field 5 - Per I (Andrzej)"), 37),
        (os.path.join(test_data_decor_path_bad, "Field 6 - Ori II (Andrzej)"), 38),
        (os.path.join(test_data_decor_path_bad, "Field 7 - VelPup I (Andrzej)"), 39),
        (os.path.join(test_data_decor_path_bad, "Field 8 - VelPic I (Andrzej)"), 20),
        (os.path.join(test_data_decor_path_bad, "Field 9"), None),
        (os.path.join(test_data_decor_path_bad, "Field 10"), 33),
        (os.path.join(test_data_decor_path_bad, "Field 11"), 25),
        (os.path.join(test_data_decor_path_bad, "Field 12"), 32),
        (os.path.join(test_data_decor_path_bad, "Field 13 (Marco)"), 19),
        (os.path.join(test_data_decor_path_bad, "Field 13 (Mike)"), 19),
        (os.path.join(test_data_decor_path_bad, "Field 14"), 12),
        (os.path.join(test_data_decor_path_bad, "Field 15"), None),
        (os.path.join(test_data_decor_path_bad, "Field 16"), 16),
        (os.path.join(test_data_decor_path_bad, "Field 17"), None),
    ],
)
def test_find_stars(path: str, expected: int):
    if expected is None:
        with pytest.raises(ValueError):
            fs.find_stars(path)
    else:
        star_observation = fs.find_stars(path)
        assert len(star_observation.stars) == expected
        for i in star_observation.stars:
            assert isinstance(i, mf.FileSystemStar)


def test_combine_star_data():
    star = fs.find_observations(
        os.path.join(test_data_with_content, "Field_1_with_content", "HD31237")
    )
    result = cb.combine_observations(star)
    assert len(result) == 2

    for satellite, setups in zip(
        [ob.SatelliteEnum.BAb, ob.SatelliteEnum.UBr], [[3, 4], [7]]
    ):
        result_filtered = [i for i in result if i.satellite == satellite][0]
        assert len(result_filtered.setup) == len(setups)
        assert all(setup in setups for setup in result_filtered.setup)

import os

import numpy as np
import pytest

from PyBriteDC.common import math as cm


@pytest.fixture
def data_array():
    return np.loadtxt(os.path.join(os.path.dirname(__file__), "testdata", "Field_1_with_content", "HD31237",
                                   "HD31237_01-Ori-I-2013_BAb_3_2_A.ndat"))[:, 0:2]

@pytest.mark.parametrize(
    "functions",
    [(cm.periodogram), (cm.calculate_rms), (cm.calculate_ptp_scatter), (cm.calculate_noise)]
)
def test_math_functions(data_array, functions):
    assert functions(data_array) is not None
    with pytest.raises(ValueError):
        functions(np.array([]))

    with pytest.raises(ValueError):
        functions(np.array([], []))

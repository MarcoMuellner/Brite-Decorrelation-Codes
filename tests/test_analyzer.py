import os
from tempfile import TemporaryDirectory

from PyBriteDC.prep import filesystem as fs
from PyBriteDC.analyzer import basics as ba
from PyBriteDC.models import file as mf, objects as ob
import pytest

test_data_with_content = os.path.join(os.path.dirname(__file__), "testdata")

@pytest.fixture
def tmp_path():
    tmpdir = TemporaryDirectory()
    yield tmpdir.name
    tmpdir.cleanup()

@pytest.mark.parametrize("path, expected", [
    (os.path.join(test_data_with_content, "Field_1_with_content"), 15),
])
def test_find_stars(tmp_path: str, path : str, expected : int):
    ba.load_field(path,tmp_path)
import os.path as path

import h5py
import pytest


@pytest.fixture(scope="session")
def test_data() -> h5py.File:
    return h5py.File(path.join(path.dirname(__file__), "test_data.h5"))

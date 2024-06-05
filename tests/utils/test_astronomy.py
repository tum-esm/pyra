import datetime
import os
import random
import sys
import tempfile
import pytest
import tum_esm_utils
from ..fixtures import sample_config

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=3)
CONFIG_DIR = os.path.join(PROJECT_DIR, "config")

sys.path.append(PROJECT_DIR)
from packages.core import types, utils


@pytest.mark.order(3)
@pytest.mark.ci
def test_astronomy(sample_config: types.Config) -> None:
    # disable test mode because in test mode it uses
    # munich coordinates instead of reading them from
    # the CamTracker config file
    sample_config.general.test_mode = False

    try:
        utils.Astronomy.get_current_sun_elevation(sample_config)
        raise Exception("Failed to warn about not loaded astronomy data.")
    except AssertionError:
        pass

    utils.Astronomy.load_astronomical_dataset()

    # use tmp camtracker config file with munich coordinates at $1 marker
    tmp_filename = tempfile.NamedTemporaryFile(delete=True).name
    with open(tmp_filename, "w") as f:
        f.write("$1\n")
        f.write("48.137154\n")
        f.write("11.576124\n")
        f.write("515\n")
    sample_config.camtracker.config_path.root = tmp_filename

    # test whether elevation is correctly computed using the config file
    e1 = utils.Astronomy.get_current_sun_elevation(sample_config)
    assert isinstance(e1, float)

    # test whether coordinates are correctly read from camtracker config file
    e2 = utils.Astronomy.get_current_sun_elevation(
        sample_config, lat=48.137154, lon=11.576124, alt=515
    )
    assert isinstance(e2, float)
    assert abs(e1 - e2) < 1e-2

    # generate a random datetime for every year between 2020 and 2050
    # and test whether the elevation is correctly computed
    for year in range(2020, 2051):
        e = utils.Astronomy.get_current_sun_elevation(
            sample_config,
            datetime_object=datetime.datetime(
                year=year,
                month=random.randint(1, 12),
                day=random.randint(1, 28),
                hour=random.randint(0, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
            ),
        )
        assert isinstance(e, float)
        assert -90 <= e <= 90

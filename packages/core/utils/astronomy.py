import os
from typing import Any, Optional
import skyfield.api
import tum_esm_utils
from packages.core import types


PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=4)


class Astronomy:
    _PLANETS: Any = None

    @staticmethod
    def load_astronomical_dataset() -> None:
        """Loads the astronomical dataset DE421 from the NASA JPL website,
        see https://ssd.jpl.nasa.gov/planets/eph_export.html."""

        filepath = os.path.join(PROJECT_DIR, "config", "astronomy_dataset_de421.bsp")
        assert os.path.isfile(filepath), "Astronomical dataset not found"

        if Astronomy._PLANETS is None:
            Astronomy._PLANETS = skyfield.api.load_file(filepath)

    @staticmethod
    def get_current_sun_elevation(config: types.ConfigDict) -> float:
        """Computes current sun elevation in degree, based on the
        coordinates from the CamTracker config file."""

        assert Astronomy._PLANETS is not None, "Astronomical dataset not loaded"
        earth = Astronomy._PLANETS["Earth"]
        sun = Astronomy._PLANETS["Sun"]

        with open(config["camtracker"]["config_path"], "r") as f:
            _lines = f.readlines()

        # find $1 marker
        _marker_line_index: Optional[int] = None
        for n, line in enumerate(_lines):
            if line == "$1\n":
                _marker_line_index = n

        assert _marker_line_index is not None, "Camtracker config file is not valid"
        lat = float(_lines[_marker_line_index + 1].strip())
        lon = float(_lines[_marker_line_index + 2].strip())
        alt = float(_lines[_marker_line_index + 3].strip())

        current_time = skyfield.api.load.timescale().now()
        current_position = earth + skyfield.api.wgs84.latlon(
            latitude_degrees=lat,
            longitude_degrees=lon,
            elevation_m=alt,
        )

        sun_pos = current_position.at(current_time).observe(sun).apparent()
        altitude, _, _ = sun_pos.altaz()
        return float(altitude.degrees)

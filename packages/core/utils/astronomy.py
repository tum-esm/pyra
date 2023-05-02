from typing import Optional
import skyfield.api
from packages.core import types

_PLANETS = skyfield.api.load("de421.bsp")
_EARTH = _PLANETS["earth"]
_SUN = _PLANETS["Sun"]


class Astronomy:
    """Provides a method to compute the current sun elevation
    based on the coordinates from the CamTracker config file."""

    @staticmethod
    def get_current_sun_elevation(config: types.ConfigDict) -> float:
        """Computes current sun elevation in degree, based on the
        coordinates from the CamTracker config file."""

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
        current_position = _EARTH + skyfield.api.wgs84.latlon(
            latitude_degrees=lat,
            longitude_degrees=lon,
            elevation_m=alt,
        )

        sun_pos = current_position.at(current_time).observe(_SUN).apparent()
        altitude, _, _ = sun_pos.altaz()
        return float(altitude.degrees)
